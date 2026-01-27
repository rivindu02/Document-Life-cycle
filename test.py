from main import Document

import pytest

# --- UNIT TESTS ---

class TestDocumentLifecycle:

    @pytest.fixture
    def doc(self):
        """Fixture to provide a fresh document for each test."""
        return Document()

    # VALID TRANSITIONS

    def test_draft_to_moderation_as_user(self, doc):
        doc.login("USER")
        doc.publish()
        assert doc.status == "MODERATION"

    def test_draft_to_published_as_admin(self, doc):
        doc.login("ADMIN")
        doc.publish()
        assert doc.status == "PUBLISHED"

    def test_moderation_to_published_as_admin(self, doc):
        doc.login("USER")
        doc.publish() # Move to Moderation
        doc.login("ADMIN")
        doc.publish() 
        assert doc.status == "PUBLISHED"    

    def test_published_to_draft_as_admin(self, doc):
        doc.login("ADMIN")
        doc.publish()   # Draft -> Published
        doc.unpublish() 
        assert doc.status == "DRAFT"

    def test_archive_from_any_state_as_admin(self, doc):
        # Test from Draft
        doc.login("ADMIN")
        doc.archive()
        assert doc.status == "ARCHIVED"
        
        # Test from Moderation
        doc2 = Document()
        doc2.login("USER")
        doc2.publish() # Now in Moderation
        doc2.login("ADMIN")
        doc2.archive()
        assert doc2.status == "ARCHIVED"

    def test_restore_archived_to_draft_as_admin(self, doc):
        doc.login("ADMIN")
        doc.archive()
        doc.restore()
        assert doc.status == "DRAFT"

    # GUARD CONDITIONS (USER , ADMIN) 

    def test_user_cannot_unpublish(self, doc):
        doc.login("ADMIN")
        doc.publish()   # Now Published
        doc.login("USER")
        doc.unpublish() # Should fail
        assert doc.status == "PUBLISHED"

    def test_user_cannot_archive(self, doc):
        doc.login("USER")
        doc.archive() # Should fail
        assert doc.status == "DRAFT"

    def test_user_cannot_publish_from_moderation(self, doc):
        doc.login("USER")
        doc.publish() # Now in Moderation
        doc.publish() # Attempting to publish again as User
        assert doc.status == "MODERATION"

    # INVALID OPERATIONS

    def test_restore_on_non_archived_doc(self, doc):
        # Document starts in Draft
        doc.login("ADMIN")
        doc.restore() # Should not change state
        assert doc.status == "DRAFT"

    def test_unpublish_on_draft(self, doc):
        doc.login("ADMIN")
        doc.unpublish() # Should stay in Draft
        assert doc.status == "DRAFT"

    def test_logout_clears_user(self, doc):
        doc.login("USER")
        doc.logout()
        doc.publish() # Should fail because user is ""
        assert doc.status == "DRAFT"
