from abc import ABC, abstractmethod

# Custom Exception for robust error handling
class DocumentError(Exception):
    """Custom exception for invalid state transitions or unauthorized actions."""
    pass

class State(ABC):
    def __init__(self, doc):
        self.doc = doc 

    @abstractmethod
    def publish(self, user): pass

    def archive(self, user):
        if user == "ADMIN":
            self.doc._transition_to(ArchivedState(self.doc))
        else:
            raise DocumentError("Only admin can archive the document.")

    def restore(self, user):
        raise DocumentError("Only archived documents can be restored.")
    
    def unpublish(self, user):
        raise DocumentError("Only published documents can be unpublished.")

# --- Context Class ---
class Document:
    def __init__(self):
        self._state = DraftState(self)
        self.currentUser = ""
    
    def login(self, user_type: str):
        if user_type in ["ADMIN", "USER"]:
            self.currentUser = user_type
        else:
            self.currentUser = ""

    def _transition_to(self, state: State):
        self._state = state
    
    def publish(self): self._state.publish(self.currentUser)
    def unpublish(self): self._state.unpublish(self.currentUser)
    def archive(self): self._state.archive(self.currentUser)
    def restore(self): self._state.restore(self.currentUser)

    @property
    def status(self):
        return self._state.__class__.__name__.replace("State", "").upper()

# --- Concrete States ---
class DraftState(State):
    def publish(self, user):
        if user == "USER":
            self.doc._transition_to(ModerationState(self.doc))
        elif user == "ADMIN":
            self.doc._transition_to(PublishedState(self.doc))
        else:
            raise DocumentError("User must be logged in to publish.")

class ModerationState(State):
    def publish(self, user):
        if user == "ADMIN":
            self.doc._transition_to(PublishedState(self.doc))
        else:
            raise DocumentError("Only admin can approve documents in moderation.")

class PublishedState(State):
    def publish(self, user):
        raise DocumentError("Document is already published.")
  
    def unpublish(self, user):
        if user == "ADMIN":
            self.doc._transition_to(DraftState(self.doc))
        else:
            raise DocumentError("Only admin can unpublish.")

class ArchivedState(State):
    def publish(self, user):
        raise DocumentError("Archived documents cannot be published. Restore them first.")
       
    def archive(self, user):
        raise DocumentError("Document is already archived.")
 
    def restore(self, user):
        if user == "ADMIN":
            self.doc._transition_to(DraftState(self.doc))
        else:
            raise DocumentError("Only admin can restore documents.")
