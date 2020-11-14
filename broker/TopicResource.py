from coapthon.resources.resource import Resource
from coapthon import defines
import re,sys,time


class TopicResource(Resource):
	def __init__(self, name="Topic",broker=None):
		"""
        	Contstructor function to create a new resource.

        	:param name: the name of the new resource
        	:param broker: the broker where the resource is stored
        	:return: tuple containing the resource and the response
        	"""
		super(TopicResource, self).__init__(name, broker, visible=True,observable=True, allow_children=False)
		self.cs = broker
		self.path = name
		self.children = []
		self.parent = None
		self.content_type = defines.Content_types["text/plain"]	#set the default to ct=0
		self.resource_type = "core.ps"
		self.payload = ""
		self.max_age = 0	


	def render_GET_advanced(self, request, response):
		"""
        	Function to handle GET requests

        	:param request: the request
        	:param response: the response
        	:return: tuple containing the resource and the response
        	"""
		sys.stdout.flush()
		#if resource has expired force the deletion and return not found
		if not self.check_age():
			response.code = defines.Codes.NOT_FOUND.number
			self.delete_resource()
			self.cs.remove_resource(self.path)
			return None,response

		if self.path =="/ps":
			response.code = defines.Codes.METHOD_NOT_ALLOWED.number
			return None,response
			
		response.payload = self.payload
		if self.max_age != 0:
			response.max_age = self.max_age
		response.code = defines.Codes.CONTENT.number
		if(request.observe == 0): # Log observe binding
			host, port = request.source
		
			if response.payload is None or response.payload=="":
				response.code = defines.Codes.NO_CONTENT.number
				response.payload = "Subscribed"
			sys.stdout.flush()    
		elif(request.observe == 1): # Log observe removing
			host, port = request.source
			response.payload = "Unsubscribed"
			response.code = defines.Codes.NO_CONTENT.number
			sys.stdout.flush()
		return self, response


	def create_topic_post(self,payload,parent_path):
		"""
        	Function to create the topic from the post payload

        	:param payload: the payload to be specified in the correct format
        	:param parent_path: the parent topic path
        	:return: tuple containing the new topic and a boolean indicating if the topic already existed
        	"""

		if payload is None or not re.match(r'^<(\w+)>((;rt=\w+)|(;if=\w+)|(;sz=\d+))*(;ct=\d+)((;rt=\w+)|(;if=\w+)|(;sz=\d+))*$',payload):
			return None,False
		topicData = payload.split(";")
		path = topicData[0][1:-1]
		exists = False
		for res in self.children:
			#if resource exists mark it in the boolean parameter
			if(res.path == parent_path+"/"+path):
				exists = True

		resource = TopicResource(parent_path+"/"+path,self.cs)
		topicData.pop(0)
		attr = {}
		attr["obs"] = ""
		for d in topicData:
			key,val = d.split("=")[0],d.split("=")[1]
			if(key == 'ct'):
				if hasattr(attr,key):
					#ct specified more than once: Error
					return None,False
				else:
					#invalid content format
					if int(val) not in [0,40,41,42,47,50,60]:
						return None,False
					elif(int(val) == 40):
						resource.allow_children = True
			attr[key] = val
		resource.attributes = attr
		sys.stdout.flush()    
		return resource, exists

	
	def render_POST_advanced(self, request, response, index = None):
		"""
        	Function to handle POST requests

        	:param request: the request
        	:param response: the response
		:param index: used to create multiple layers (represents the index of the resource from which to start in the hierarchy)
        	:return: tuple containing the resource and the response
        	"""
		#create multiple topics
		if index is not None:
			parent_res,response = self.create_subtopics(request,response,index)
			if parent_res is None:
				return None, response
			method = getattr(parent_res, "render_POST_advanced", None)
			#call the render_POST of the new parent resource created
			return method(request=request,response=response,index=None)

		child_res,exists = self.create_topic_post(request.payload,self.path)
		#something went wrong: BAD REQUEST
		if(child_res is None):
			response.payload = "Bad Request"
			response.code = defines.Codes.BAD_REQUEST.number
			return self,response
		child_res.parent = self
		
		# The resource already exists: modify it
		if(exists):
			old_res = self.cs.root[child_res.path]
			if(len(old_res.children)>0 and not child_res.allow_children):
				delete_tree(old_res,False)
			old_res.attributes = child_res.attributes
			old_res.allow_children = child_res.allow_children
			if not old_res.check_content_type(old_res.payload):
				old_res.payload = ""
			response.code = defines.Codes.CHANGED.number
			response.payload = old_res.path + " Modified"
			if request.max_age is not None:
				child_res.max_age = time.time()+int(request.max_age)
			return self,response
			
		#check if the parent resource admits a child (ct=40)
		if(not self.allow_children):
			response.code = defines.Codes.FORBIDDEN.number
			response.payload = self.path + " cannot have children"
			return self, response
		
		#set the max_age
		if request.max_age is not None:
			child_res.max_age = time.time()+int(request.max_age)

		self.children.append(child_res)
		self.cs.add_resource(child_res.path,child_res)

		response.payload = "Created. Location: "+child_res.path 
		response.location_path = child_res.path
		response.code = defines.Codes.CREATED.number
		print("[BROKER] Resource "+child_res.path+" created.");
		sys.stdout.flush()            
		return self,response
	
	#used to implement POST or PUT to nonexisting topics: create all the nonexisting subtopics and return the leaf topic
	def create_subtopics(self,request,response,index, update=False):
		"""
        	Function to handle POST and PUT to nonexisting topic, used to create all the needed sublayers

        	:param request: the request
        	:param response: the response
		:param index: used to indicate the index of the resource from which to start in the hierarchy of topics
		:param update: boolean parameter indicating that the last topic need to contain the value (PUBLISH)
        	:return: tuple containing the new topic and a boolean indicating if the topic already existed
        	"""
		path = request.uri_path
		topics = path.split("/")
		base = self.path
		old_res = self
		max_age = 0
		if request.max_age is not None:
			max_age = time.time()+int(request.max_age)

		if(not self.allow_children):
			response.code = defines.Codes.FORBIDDEN.number
			response.payload = self.path + " cannot have children"
			return None,response

		for i in range(index,len(topics)):
			new_res = TopicResource(base+"/"+topics[i],self.cs)
			new_res.max_age = max_age
			new_res.parent = old_res
			if(i<len(topics)-1):
				new_res.content_type = defines.Content_types["application/link-format"]
				new_res.allow_children = True
				self.cs.add_resource(new_res.path,new_res)
			old_res.children.append(new_res)
			base = base+"/"+topics[i]
			old_res = new_res
		#this means it is a PUT request (create on publish)(it is possible to use the request.code too)
		if(update):
			new_res.payload = request.payload
			response.payload = "Created. Location: "+new_res.path
			response.location_path = new_res.path
			new_res.content_type = defines.Content_types["text/plain"]
		else:
			new_res.content_type = defines.Content_types["application/link-format"]
			new_res.allow_children = True
		new_res.max_age = max_age
		self.cs.add_resource(new_res.path,new_res)
		
		response.code = defines.Codes.CREATED.number
		sys.stdout.flush()
		#returns the last created resource
		return new_res,response

	def render_PUT_advanced(self, request, response, index = None):
		"""
        	Function to handle PUT requests.

        	:param request: the request
        	:param response: the response
		:param index: used to create multiple layers (represents the index of the resource from which to start in the hierarchy)
        	:return: tuple containing the resource and the response
        	"""
		#create on publish	
		if index is not None:
			return self.create_subtopics(request, response, index, True)
		sys.stdout.flush()
		if not self.check_age():
			self.payload = request.payload
			self.allow_children = False
			self.content_type = defines.Content_types["text/plain"]
			delete_tree(self,False)
			if request.max_age is not None:
				self.max_age = time.time()+int(request.max_age)
			else:
				self.max_age = 0
			response.code = defines.Codes.CREATED.number
			response.payload = "Created"
			response.location_path = self.path
			return self,response
		# Forbid updating the base ps api resource         
		if(request.uri_path == "ps"):
			response.code = defines.Codes.FORBIDDEN.number
			response.payload = "Forbidden"
			return False, response        
		if not self.check_content_type(request.payload):
			response.code = defines.Codes.BAD_REQUEST.number
			response.payload = "Unacceptable content format."
			return False,response
		self.payload = request.payload
		
		if request.max_age is not None:
			self.max_age = time.time()+int(request.max_age)
		sys.stdout.flush()
		response.payload = "Changed"
		response.code = defines.Codes.CHANGED.number
		return self, response


	def render_DELETE_advanced(self, request, response):
		"""
        	Function to handle DELETE requests

        	:param request: the request
        	:param response: the response
		:return: tuple containing a boolean indicating the outcome of the request and the response
        	"""
		if(request.uri_path == "ps"):
			response.code = defines.Codes.FORBIDDEN.number
			response.payload = "Forbidden"            
			return False, response
		response.payload = "Deleted"
		response.code = defines.Codes.DELETED.number
		sys.stdout.flush()    
		if(len(self.children)>0):
			delete_tree(self,False)
		if(self.parent):
			try:
				self.parent.remove_children(self.path)
			except:
				pass
		return True, response


	
	def check_content_type(self,payload):
		"""
		Function to check if the input is compatible with the resource
		content format specified at the creation. ct=0 allows any string, ct=50 allows only JSON. Add here the support to other content-formats

		:param payload: the payload to check
		:return: a boolean indicating the payload is compatible with the resource content type
		"""
		#this means it's a JSON
		if re.match(r'^{\"\w+\"\:((\w+)|(\"\w+\"))(,\"\w+\"\:((\"\w+\")|(\w+)))*}$',payload):
			if int(self.actual_content_type) in [defines.Content_types["text/plain"], defines.Content_types["application/json"]]:
				return True
		else:
			if int(self.actual_content_type) ==defines.Content_types["text/plain"]: 
				return True
		return False

	def remove_children(self,child_path):
		for ch in self.children:
			if ch.path == child_path:
				self.children.remove(ch)
	
	def delete_resource(self):
		if(self.parent):
			try:
				self.parent.remove_children(self.path)
			except:
				pass
		if(len(self.children)>0):
			delete_tree(self,False)
		return True

	def check_age(self):
		"""
		Function that checks if the max_age of the resource is not expired

		return: a boolean
		"""
		
		return (self.max_age is None or self.max_age==0 or self.max_age > time.time())

def delete_tree(root_resource,toDelete=True):
	"""
        Function to delete the tree rooted at the resource in the input

        :param root_resource: the root of the tree
        :param toDelete: boolean to specify if the roots needs to be deleted or not
        :return: None
        """
	for child in root_resource.children:
		#root_resource.children.remove(child)
		delete_tree(child)
	#root_resource.parent.children.remove(root_resource)
	root_resource.children = []
	if(toDelete):
		root_resource.cs.remove_resource(root_resource.path)


