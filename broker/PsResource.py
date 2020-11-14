from coapthon.resources.resource import Resource
from coapthon import defines
import re,sys,json,time
"""
	Delete the entire subtree of a resource if it has children,
	by recursive iteration of the subtree of root root_resource.
	If base is true, the deletion will be performed by the calling
	method, otherwise the deletion will be performed by the function
"""

def delete_subtree_old(root_resource,base=False):
	if(len(root_resource.children) == 0):
		print("SONO QUI:"+root_resource.name)
		print("[BROKER] Deleting: "+root_resource.name)
		root_resource.cs.remove_resource(root_resource.name)
		return
	for l in root_resource.children:
		print("SONO QUI:"+l.name)
		delete_subtree(l,False)
		return
		print("[BROKER] Removing from children: "+l.name)
		#root_resource.children.remove(l)
		if(len(root_resource.children) == 0 and not base):
			print("[BROKER] Deleting: "+root_resource.name)
			root_resource.cs.remove_resource(root_resource.name)
			break

	#notify all subscribers that the resource has been deleted			
	#root_resource.cs.notify(root_resource,True)
 

def delete_subtree(root_resource,toDelete=True):
	for child in root_resource.children:
		print("[Broker] Deleting subtree of: "+child.path)
		#root_resource.children.remove(child)
		delete_subtree(child)
	#root_resource.parent.children.remove(root_resource)
	root_resource.children = []
	if(toDelete):
		print("[Broker] Deleting resource: "+root_resource.path)
		root_resource.cs.remove_resource(root_resource.path)




"""
	Base resource for the Publish/Subsribe topic.
	Follows the Composite Design Pattern to maintain a recursive list 
	of children.
"""
class PsResource(Resource):
	def __init__(self, name="/ps",coap_server=None,):
		super(PsResource, self).__init__(name, coap_server, visible=True,observable=True, allow_children=False)
		self.cs = coap_server
		self.resource_type = "core.ps" # draft stabdard
		self.content_type = defines.Content_types["text/plain"]
		self.payload = ""
		self.children = []
		self.parent = None
		self.max_age = 0
		self.path = name
		#self.attributes["ct"]=0
	"""
		Handle get requests: observe requests are internally served
		by CoAPthon itself. 
	"""
	def render_GET_advanced(self, request, response):
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
		response.max_age = self.max_age
		response.code = defines.Codes.CONTENT.number
		if(request.observe == 0): # Log observe binding
			host, port = request.source
		
			if response.payload is None or response.payload=="":
				response.code = defines.Codes.NO_CONTENT.number
				response.payload = "Subscribed."
			print("[BROKER] Binding observe for: "+host+" to "+self.path)
			sys.stdout.flush()    
		elif(request.observe == 1): # Log observe removing
			host, port = request.source
			response.payload = "Unsubscribed."
			response.code = defines.Codes.NO_CONTENT.number
			print("[BROKER] Removing observe for: "+host+" to "+self.path)
			sys.stdout.flush()
		return self, response

	"""
		Create a resource from the POST payload for the base url.
		Returns None if he request is BAD
		Returns another existant resource in case of duplicates
	"""
	def create_res_from_payload(self,payload,base):
		#RegEx to check if the format of the request is RFC compliant (also according to CoAPthon defines)

		if (payload is None or not re.match(r'^<(\w+)>((;rt=\w+)|(;if=\w+)|(;sz=\d+))*(;ct=\d+)((;rt=\w+)|(;if=\w+)|(;sz=\d+))*$',payload)):
		#if(payload is None or not re.match(r'^<(\w+)>;(?:(ct=\w+;)|(rt=\w+;)|(if=\w+;)|(sz=\w+;))+$',payload)):
			return None,False
		topicData = payload.split(";")
		topicPath = topicData[0]
		path = topicPath.replace("<","").replace(">","")
		exists = False
		for res in self.children:
			if(res.path == base+"/"+path):
				#RESROUCE ALREADY EXISTS
				#return res
				exists = True
		# Create new Ps Resource with the new uri path
		resource = PsResource(base+"/"+path,self.cs)
		topicData.pop(0)
		attr = {}
		attr["obs"] = ""
		# Extract and build the attribute object for the new Resource
		for d in topicData:
			key,val = d.split("=")[0],d.split("=")[1]
			print("[BROKER] Attr: "+key+" Val:"+val)
			if(key == 'ct'):
				#ct specified more than once
				if hasattr(attr,key):
					return None,False
				else:	
					#invalid content format
					if int(val) not in [0,40,41,42,47,50,60]:
						return None,False
					elif(int(val) == 40):
						resource.allow_children = True
					#val = [val]
			attr[key] = val
		resource.attributes = attr
		sys.stdout.flush()    
		return resource, exists

	
	"""
		Handle POST request to create resource on this path
	"""
	def render_POST_advanced(self, request, response, index = None):
		
		#create multiple topics
		if index is not None:
			parent_res,response = self.create_subtopics(request,response,index)
			if parent_res is None:
				return None, response
			method = getattr(parent_res, "render_POST_advanced", None)
			#call the render_POST of the new parent resource created
			return method(request=request,response=response,index=None)

		child_res,exists = self.create_res_from_payload(request.payload,self.path)
		# The request is not formatted according to RFC
		if(child_res is None):
			response.code = defines.Codes.BAD_REQUEST.number
			response.payload = "Bad Request"
			return self,response
		child_res.parent = self
		
		# The resource already exists at this topic
		
		if(exists):
			old_res = self.cs.root[child_res.path]
			if(len(old_res.children)>0 and not child_res.allow_children):
				delete_subtree(old_res,False)
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
	
	#used to implement POST or PUT to nonexisting topics: create the nonexisting subtopics and return the leaf topic
	def create_subtopics(self,request,response,index, update=False):
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
			new_res = PsResource(base+"/"+topics[i],self.cs)
			new_res.max_age = max_age
			new_res.parent = old_res
			if(i<len(topics)-1):
				#new_res.attributes["ct"] = 40
				new_res.content_type = defines.Content_types["application/link-format"]
				new_res.allow_children = True
				self.cs.add_resource(new_res.path,new_res)
			old_res.children.append(new_res)
			base = base+"/"+topics[i]
			old_res = new_res
		#this means it is a PUT request (create on publish)
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

	"""
		Handle PUT requests to the resource
		- If resource exists it update the payload
		- Otherwise the modified internal implementation of CoAPthon creates a new resource
	"""
	def render_PUT_advanced(self, request, response, index = None):
		
		#create on publish	
		if index is not None:
			return self.create_subtopics(request, response, index, True)
		sys.stdout.flush()
		if not self.check_age():
			self.payload = request.payload
			self.allow_children = False
			#self.attributes["ct"] = 0
			self.content_type = defines.Content_types["text/plain"]
			delete_subtree(self,False)
			if request.max_age is not None:
				self.max_age = time.time()+int(request.max_age)
			else:
				self.max_age = 0
			response.code = defines.Codes.CREATED.number
			response.payload = "Created. Location: "+self.path
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

		print("[BROKER] "+self.path+" updated with content: "+request.payload)
		sys.stdout.flush()
		response.payload = "Changed"
		response.code = defines.Codes.CHANGED.number
		return self, response

	"""
		Handles resource DELETION as well as deletion
		of possibly present children with a recursive deletion
		at the end of the recursive deletion, it deletes the resource from the parent children.
		Returns True if all goes good so that coapthon can delete the subtree root resource.
	"""
	def render_DELETE_advanced(self, request, response):
		if(request.uri_path == "ps"):
			response.code = defines.Codes.FORBIDDEN.number
			response.payload = "Forbidden"            
			return False, response
		response.payload = "Deleted"
		response.code = defines.Codes.DELETED.number
		print("[BROKER] Deleting subtree of "+self.path)
		sys.stdout.flush()    
		if(len(self.children)>0):
			delete_subtree(self,False)
		if(self.parent):
			try:
				self.parent.remove_children(self.path)
			except:
				pass
		return True, response


	"""
		Check if the input is compatible with the resource
		content format specified at the creation.
		-Ct=0 allows any string
		-Ct=50 allows only JSON
		-Others don't accept anything
	"""
	def check_content_type(self,payload):
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
			delete_subtree(self,False)
		return True

	def check_age(self):
		return (self.max_age is None or self.max_age==0 or self.max_age > time.time())



