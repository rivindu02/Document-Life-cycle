from main import Document

import pytest

# --- UNIT TESTS ---

# COMPREHENSIVE TEST SUITE - STATE TRANSITION TESTING
class TestDocumentLifecycle:
    """
    Comprehensive state transition testing covering:
    - All valid transitions (8)
    - All invalid transitions (16)
    - Guard condition boundaries (ADMIN vs USER)
    - Error message validation
    """

    @pytest.fixture
    def doc(self):
        """Fixture providing a fresh Document instance for each test."""
        return Document()

    # VALID TRANSITIONS - Testing all 8 valid state transitions

    def test_valid_draft_to_moderation_user(self, doc):
        """Valid: DRAFT --[publish() as USER]--> MODERATION"""
        doc.login("USER")
        doc.publish()
        assert doc.status == "MODERATION"

    def test_valid_draft_to_published_admin(self, doc):
        """Valid: DRAFT --[publish() as ADMIN]--> PUBLISHED"""
        doc.login("ADMIN")
        doc.publish()
        assert doc.status == "PUBLISHED"

    def test_valid_draft_to_archived_admin(self, doc):
        """Valid: DRAFT --[archive() as ADMIN]--> ARCHIVED"""
        doc.login("ADMIN")
        doc.archive()
        assert doc.status == "ARCHIVED"

    def test_valid_moderation_to_published_admin(self, doc):
        """Valid: MODERATION --[publish() as ADMIN]--> PUBLISHED"""
        doc.login("USER")
        doc.publish()  # DRAFT --> MODERATION
        doc.login("ADMIN")
        doc.publish()  # MODERATION --> PUBLISHED
        assert doc.status == "PUBLISHED"

    def test_valid_moderation_to_archived_admin(self, doc):
        """Valid: MODERATION --[archive() as ADMIN]--> ARCHIVED"""
        doc.login("USER")
        doc.publish()  # DRAFT --> MODERATION
        doc.login("ADMIN")
        doc.archive()  # MODERATION --> ARCHIVED
        assert doc.status == "ARCHIVED"

    def test_valid_published_to_draft_admin(self, doc):
        """Valid: PUBLISHED --[unpublish() as ADMIN]--> DRAFT"""
        doc.login("ADMIN")
        doc.publish()    # DRAFT --> PUBLISHED
        doc.unpublish()  # PUBLISHED --> DRAFT
        assert doc.status == "DRAFT"

    def test_valid_published_to_archived_admin(self, doc):
        """Valid: PUBLISHED --[archive() as ADMIN]--> ARCHIVED"""
        doc.login("ADMIN")
        doc.publish()  # DRAFT --> PUBLISHED
        doc.archive()  # PUBLISHED --> ARCHIVED
        assert doc.status == "ARCHIVED"

    def test_valid_archived_to_draft_admin(self, doc):
        """Valid: ARCHIVED --[restore() as ADMIN]--> DRAFT"""
        doc.login("ADMIN")
        doc.archive()  # DRAFT --> ARCHIVED
        doc.restore()  # ARCHIVED --> DRAFT
        assert doc.status == "DRAFT"

    
    # INVALID TRANSITIONS - FROM DRAFT STATE (4 invalid operations)
    

    def test_invalid_draft_publish_no_login(self, doc):
        """Invalid: DRAFT --[publish() no login]--> Error"""
        # No login, currentUser is empty
        with pytest.raises(DocumentError, match="User must be logged in to publish"):
            doc.publish()
        assert doc.status == "DRAFT"  # State unchanged

    def test_invalid_draft_unpublish(self, doc):
        """Invalid: DRAFT --[unpublish()]--> Error"""
        doc.login("ADMIN")
        with pytest.raises(DocumentError, match="Only published documents can be unpublished"):
            doc.unpublish()
        assert doc.status == "DRAFT"

    def test_invalid_draft_archive_user(self, doc):
        """Invalid: DRAFT --[archive() as USER]--> Error (guard condition)"""
        doc.login("USER")
        with pytest.raises(DocumentError, match="Only admin can archive"):
            doc.archive()
        assert doc.status == "DRAFT"

    def test_invalid_draft_restore(self, doc):
        """Invalid: DRAFT --[restore()]--> Error"""
        doc.login("ADMIN")
        with pytest.raises(DocumentError, match="Only archived documents can be restored"):
            doc.restore()
        assert doc.status == "DRAFT"

    
    # INVALID TRANSITIONS - FROM MODERATION STATE (4 invalid operations)
    

    def test_invalid_moderation_publish_user(self, doc):
        """Invalid: MODERATION --[publish() as USER]--> Error (guard condition)"""
        doc.login("USER")
        doc.publish()  # DRAFT --> MODERATION
        with pytest.raises(DocumentError, match="Only admin can approve documents in moderation"):
            doc.publish()
        assert doc.status == "MODERATION"

    def test_invalid_moderation_publish_no_login(self, doc):
        """Invalid: MODERATION --[publish() no login]--> Error"""
        doc.login("USER")
        doc.publish()  # DRAFT --> MODERATION
        doc.login("")  # Logout
        with pytest.raises(DocumentError, match="Only admin can approve"):
            doc.publish()
        assert doc.status == "MODERATION"

    def test_invalid_moderation_unpublish(self, doc):
        """Invalid: MODERATION --[unpublish()]--> Error"""
        doc.login("USER")
        doc.publish()  # DRAFT --> MODERATION
        doc.login("ADMIN")
        with pytest.raises(DocumentError, match="Only published documents can be unpublished"):
            doc.unpublish()
        assert doc.status == "MODERATION"

    def test_invalid_moderation_restore(self, doc):
        """Invalid: MODERATION --[restore()]--> Error"""
        doc.login("USER")
        doc.publish()  # DRAFT --> MODERATION
        doc.login("ADMIN")
        with pytest.raises(DocumentError, match="Only archived documents can be restored"):
            doc.restore()
        assert doc.status == "MODERATION"

    def test_invalid_moderation_archive_user(self, doc):
        """Invalid: MODERATION --[archive() as USER]--> Error (guard condition)"""
        doc.login("USER")
        doc.publish()  # DRAFT --> MODERATION
        with pytest.raises(DocumentError, match="Only admin can archive"):
            doc.archive()
        assert doc.status == "MODERATION"

    
    # INVALID TRANSITIONS - FROM PUBLISHED STATE (4 invalid operations)
    

    def test_invalid_published_publish_admin(self, doc):
        """Invalid: PUBLISHED --[publish() as ADMIN]--> Error"""
        doc.login("ADMIN")
        doc.publish()  # DRAFT --> PUBLISHED
        with pytest.raises(DocumentError, match="Document is already published"):
            doc.publish()
        assert doc.status == "PUBLISHED"

    def test_invalid_published_publish_user(self, doc):
        """Invalid: PUBLISHED --[publish() as USER]--> Error"""
        doc.login("ADMIN")
        doc.publish()  # DRAFT --> PUBLISHED
        doc.login("USER")
        with pytest.raises(DocumentError, match="Document is already published"):
            doc.publish()
        assert doc.status == "PUBLISHED"

    def test_invalid_published_unpublish_user(self, doc):
        """Invalid: PUBLISHED --[unpublish() as USER]--> Error (guard condition)"""
        doc.login("ADMIN")
        doc.publish()  # DRAFT --> PUBLISHED
        doc.login("USER")
        with pytest.raises(DocumentError, match="Only admin can unpublish"):
            doc.unpublish()
        assert doc.status == "PUBLISHED"

    def test_invalid_published_restore(self, doc):
        """Invalid: PUBLISHED --[restore()]--> Error"""
        doc.login("ADMIN")
        doc.publish()  # DRAFT --> PUBLISHED
        with pytest.raises(DocumentError, match="Only archived documents can be restored"):
            doc.restore()
        assert doc.status == "PUBLISHED"

    def test_invalid_published_archive_user(self, doc):
        """Invalid: PUBLISHED --[archive() as USER]--> Error (guard condition)"""
        doc.login("ADMIN")
        doc.publish()  # DRAFT --> PUBLISHED
        doc.login("USER")
        with pytest.raises(DocumentError, match="Only admin can archive"):
            doc.archive()
        assert doc.status == "PUBLISHED"

    
    # INVALID TRANSITIONS - FROM ARCHIVED STATE (4 invalid operations)

    def test_invalid_archived_publish_admin(self, doc):
        """Invalid: ARCHIVED --[publish() as ADMIN]--> Error"""
        doc.login("ADMIN")
        doc.archive()  # DRAFT --> ARCHIVED
        with pytest.raises(DocumentError, match="Restore them first"):
            doc.publish()
        assert doc.status == "ARCHIVED"

    def test_invalid_archived_publish_user(self, doc):
        """Invalid: ARCHIVED --[publish() as USER]--> Error"""
        doc.login("ADMIN")
        doc.archive()  # DRAFT --> ARCHIVED
        doc.login("USER")
        with pytest.raises(DocumentError, match="Restore them first"):
            doc.publish()
        assert doc.status == "ARCHIVED"

    def test_invalid_archived_unpublish(self, doc):
        """Invalid: ARCHIVED --[unpublish()]--> Error"""
        doc.login("ADMIN")
        doc.archive()  # DRAFT --> ARCHIVED
        with pytest.raises(DocumentError, match="Only published documents can be unpublished"):
            doc.unpublish()
        assert doc.status == "ARCHIVED"

    def test_invalid_archived_archive_admin(self, doc):
        """Invalid: ARCHIVED --[archive() as ADMIN]--> Error"""
        doc.login("ADMIN")
        doc.archive()  # DRAFT --> ARCHIVED
        with pytest.raises(DocumentError, match="Document is already archived"):
            doc.archive()
        assert doc.status == "ARCHIVED"

    def test_invalid_archived_restore_user(self, doc):
        """Invalid: ARCHIVED --[restore() as USER]--> Error (guard condition)"""
        doc.login("ADMIN")
        doc.archive()  # DRAFT --> ARCHIVED
        doc.login("USER")
        with pytest.raises(DocumentError, match="Only admin can restore"):
            doc.restore()
        assert doc.status == "ARCHIVED"

    
    # SECURITY & BOUNDARY TESTS - Guard conditions and edge cases
    

    def test_login_logout_security(self, doc):
        """Test that logout prevents unauthorized actions"""
        doc.login("USER")
        doc.publish()  # DRAFT --> MODERATION
        
        doc.login("")  # Logout
        with pytest.raises(DocumentError):
            doc.publish()  # Should fail - no user logged in
        
        assert doc.status == "MODERATION"  # State unchanged

    def test_role_switching_security(self, doc):
        """Test that role changes are properly enforced"""
        doc.login("ADMIN")
        doc.publish()  # DRAFT --> PUBLISHED
        
        # Switch to USER - should not be able to unpublish
        doc.login("USER")
        with pytest.raises(DocumentError, match="Only admin can unpublish"):
            doc.unpublish()
        
        assert doc.status == "PUBLISHED"

    def test_invalid_login_type(self, doc):
        """Test that invalid login types don't grant privileges"""
        doc.login("INVALID_ROLE")
        
        with pytest.raises(DocumentError, match="User must be logged in"):
            doc.publish()
        
        assert doc.status == "DRAFT"
