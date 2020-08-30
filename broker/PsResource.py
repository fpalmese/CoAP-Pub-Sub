from coapthon.resources.resource import Resource
from coapthon import defines
import re
import sys
"""
	Delete the entire subtree of a resource if it has children,
	by recursive iteration of the subtree of root root_resource.
	If base is true, the deletion will be performed by the calling
	method, otherwise the deletion will be performed by the function
"""
def delete_subtree(root_resource,base=False):
	if(len(root_resource.children) == 0):
		print("[BROKER] Deleting: "+root_resource.name)
		root_resource.cs.remove_resource(root_resource.name)
		return
	for l in root_resource.children:
		delete_subtree(l)
		print("[BROKER] Removing from children: "+l.name)
		root_resource.children.remove(l)
		if(len(root_resource.children) == 0 and not base):
			print("[BROKER] Deleting: "+root_resource.name)
			root_resource.cs.remove_resource(root_resource.name)
			break      
	#notify all subscribers that the resource has been deleted			
	root_resource.cs.notify(root_resource,True)
 
	
"""
	Base resource for the Publish/Subsribe topic.
	Follows the Composite Design Pattern to maintain a recursive list 
	of children.
"""
class PsResource(Resource):
	def __init__(self, name="PsResource",coap_server=None):
		super(PsResource, self).__init__(name, coap_server, visible=True,observable=True, allow_children=True)
		self.cs = coap_server
		self.resource_type = "core.ps" # draft stabdard
		self.content_type = "text/plain"
		self.payload = ""
		self.children = []
		self.parent = None

	"""
		Handle get requests: observe requests are internally served
		by CoAPthon itself. 
	"""
	def render_GET_advanced(self, request, response):
		sys.stdout.flush();           
		response.payload = self.payload
		response.code = defines.Codes.CONTENT.number
		if(request.observe == 0): # Log observe biding
			host, port = request.source
			print("[BROKER] Binding observe to: "+host)
			sys.stdout.flush()    
		return self, response

	"""
		Create a resource from the POST payload for the base url.
		Returns None if he request is BAD
		Returns another existant resource in case of duplicates
	"""
	def createResFromPayload(self,payload,base):
		#RegEx to check if the format of the request is RFC compliant (also according to CoAPthon defines)
		if(payload is None or not re.match(r'^<(\w+)>;(?:(ct=\w+;)|(rt=\w+;)|(if=\w+;)|(sz=\w+;))+$',payload)):
			return None
		payload = payload[:-1]
		topicData = payload.split(";")
		topicPath = topicData[0]
		path = topicPath.replace("<","").replace(">","")
		for res in self.children:
			if(res.name == base+"/"+path):
				#RESROUCE ALREADY EXISTS
				return res
		# Create new Ps Resource with the new uri path
		resource = PsResource(base+"/"+path,self.cs)
		resource.allow_children = False
		topicData.pop(0);
		attr = {}
		attr["obs"] = ""
		# Extract and build the attribute object for the new Resource
		for d in topicData:
			key,val = d.split("=")[0],d.split("=")[1]
			print("[BROKER] Attr: "+key+" Val:"+val)
			if(key == 'ct'):
				if(val == '40'):
					resource.allow_children = True
				val = [val]
			attr[key] = val
		resource.attributes = attr
		sys.stdout.flush()    
		return resource

	
	"""
		Handle POST request to create resource on this path
	"""
	def render_POST_advanced(self, request, response):
		child_res = self.createResFromPayload(request.payload,"/"+request.uri_path)
		# The request is not formatted according to RFC
		if(child_res is None):
			response.code = defines.Codes.BAD_REQUEST.number
			response.payload = "Bad Request"
			return self,response
		child_res.parent = self
		
		# The resource already exists at this topic
			
		if(child_res in self.children):
			response.code = defines.Codes.FORBIDDEN.number
			response.payload = child_res.name + " Already Exists"
			return self,response
		"""
		if(self.containsChild(child_res.name)):
			response.code = defines.Codes.FORBIDDEN.number
			response.payload = child_res.name + " Already Exists"
			return self,response
		"""
		#check if the parent resource admits a child (ct=40)
		if(not self.allow_children):
			response.code = defines.Codes.FORBIDDEN.number
			response.payload = self.name + " cannot have children"
			return self, response

		self.children.append(child_res)
		self.cs.add_resource(child_res.name,child_res)

		response.payload = child_res.name + " Created"
		response.code = defines.Codes.CREATED.number
		print("[BROKER] Resource "+child_res.name+" created.");
		sys.stdout.flush()            
		return self,response



	def createOnPublish(self,request,response,index):
		path = request.uri_path
		topics = path.split("/")
		base = self.path
		old_res = self
		if(not self.allow_children):
			response.code = defines.Codes.FORBIDDEN.number
			response.payload = self.name + " cannot have children"
			return None,response

		for i in range(index,len(topics)):
			new_res = PsResource(base+"/"+topics[i],self.cs)
			new_res.parent = old_res
			if(i<len(topics)-1):
				new_res.attributes["ct"] = ["40"]
				new_res.allow_children = True
				self.cs.add_resource(new_res.name,new_res)
			old_res.children.append(new_res)
			base = base+"/"+topics[i]
			old_res = new_res

		new_res.payload = request.payload
		new_res.allow_children = False
		self.cs.add_resource(new_res.name,new_res)
		response.payload = "Created"
		response.code = defines.Codes.CREATED.number
		sys.stdout.flush()
		return new_res,response



	"""
		Handle PUT requests to the resource
		- If resource exists it update the payload
		- Otherwise the modified internal implementation of CoAPthon creates a new resource
	"""
	def render_PUT_advanced(self, request, response, index = None):
		
		#create on publish	
		if index is not None:
			return self.createOnPublish(request, response, index)

		sys.stdout.flush()           
		# Forbid updating the base ps api resource         
		if(request.uri_path == "ps"):
			response.code = defines.Codes.FORBIDDEN.number
			response.payload = "Forbidden"
			return False, response        
		self.payload = request.payload
		print("[BROKER] "+self.name+" updated with content: "+request.payload)
		sys.stdout.flush()            
		# New resource has been created before passing control to this method
		"""if(response.code == defines.Codes.CREATED.number): 
			response.payload = "Created"
			return self,response
		"""
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
		print("[BROKER] Deleting subtree of "+self.name)
		sys.stdout.flush()    
		if(len(self.children)>0):
			delete_subtree(self,True)
		if(self.parent):
			self.parent.children.remove(self)
		return True, response


