#status = "PUBLISHED" or "DRAFT" or "MODERATION" or "ARCHIVED"
#currentUser = "USER" or "ADMIN" or ""
from abc import ABC, abstractmethod

# State Interface/Abstract Class -declares the state-specific methods that all Concrete States should implement.
class State(ABC):
    def __init__(self, doc):
        self.doc = doc 

    @abstractmethod
    def publish(self,user): pass

    #@abstractmethod---> Forces every child class to implement its own version of the method. If a child class doesn't implement it, Python will raise an error when you try to instantiate that child.
    # Regular Method (Concrete): If you define a method without the decorator, child classes will inherit that logic automatically. They only need to override it if they need to do something different (like the ArchivedState,RestoredState,UnpublishedState here). {This is a optimization from Template Method Pattern.}
    def archive(self,user): # this is the default method for Draft, Published, Moderation statuses
        match user:
            case "ADMIN":
                print('Document archived by admin')
                #self.doc._state = ArchivedState(self.doc)
                self.doc._transition_to(ArchivedState(self.doc))
            case _:
                print('Only admin can archive the document')

    def restore(self,user):
        print('Only archived documents can be restored')
    
    def unpublish(self,user):
        print('Only published documents can be unpublished')

    
# Context Class- (Document) stores a reference to its current concrete state object.
class Document:
    def __init__(self):
        self._state =DraftState(self)  #Using self.status is fine, but since it holds an object and not a string, it might be slightly confusing to someone reading the code.
        self.currentUser = ""
    
    def login(self, userType: str):
        if (userType in ["ADMIN","USER"]):
           print(f'User logged in as {userType}')
           self.currentUser = userType
        else:
           print('Invalid user type')
           self.currentUser = ""
        return self.currentUser


    def logout(self):
       print('User logged out')
       self.currentUser = ""
       return self.currentUser
    
    # PRIVATE TRANSITION METHOD--> before to change state have to modify private/protected variable directly
    def _transition_to(self, state: State):
        print(f"Transitioning to {state.__class__.__name__}")
        self._state = state
    
    def get_state(self): return self._state
    
    def publish(self): self._state.publish(self.currentUser)
    
    def unpublish(self): self._state.unpublish(self.currentUser)
    
    def archive(self): self._state.archive(self.currentUser)
    
    def restore(self): self._state.restore(self.currentUser)

    @property       # for make this more readable
    def status(self):
        return self._state.__class__.__name__.replace("State", "").upper()

# Concrete States - provide specific implementations for the state-specific methods defined in the State interface.
class DraftState(State):
    def publish(self,user):
        match user:
            case "USER":
                print('Document sent for moderation')
                #self.doc._state = ModerationState(self.doc)
                self.doc._transition_to(ModerationState(self.doc))
            case "ADMIN":
                print('Document published and is now live')
                #self.doc._state = PublishedState(self.doc)
                self.doc._transition_to(PublishedState(self.doc))
            case _:
                print('Only logged in users can publish the document')
  
       

class ModerationState(State):
    def publish(self,user):
        match user:
            case "ADMIN":
                print('Document published by admin and is now live')
                #self.doc._state = PublishedState(self.doc)
                self.doc._transition_to(PublishedState(self.doc))
            case _:
                print('Only admin can publish the document from moderation')
  
 

class PublishedState(State):
    def publish(self,user):
        print('Document is already published and live')
  
    def unpublish(self,user):
        match user:
            case "ADMIN":
                print('Document unpublished by admin and is now in Draft state')
                #self.doc._state = DraftState(self.doc)
                self.doc._transition_to(DraftState(self.doc))
            case _:
                print('Only admin can unpublish the document')
 


class ArchivedState(State):
    def publish(self,user):
        print('Archived document cannot be published, first restore the document')
       
    def archive(self,user):
        print('Document is already archived')
 
    def restore(self,user):
        match user:
            case "ADMIN":
                print('Document restored by admin and is now in Draft state')
                #self.doc._state = DraftState(self.doc)
                self.doc._transition_to(DraftState(self.doc))
            case _:
                print('Only admin can restore the document from archived state')




# Python doesn't have true private members like other languages. It uses naming conventions:

# No underscore (name) = Public
# Single underscore (_name) = Protected (internal use, but accessible)
# Double underscore (__name) = Name mangling (closest to "private")
# GOOD: Using the public interface



## Design Best Practice Example

# doc = Document()
# doc.login("ADMIN")
# doc.publish()  # Uses current user automatically ******Dynamic Method Resolution

# # DISCOURAGED: Direct state manipulation
# doc._state = PublishedState(doc)  # Bypasses transition logic

# # BETTER: Using centralized transition
# doc._transition_to(PublishedState(doc))  # Includes logging and validation
