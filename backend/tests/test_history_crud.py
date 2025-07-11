import unittest
import json
from sqlalchemy.orm import Session

from backend.models import UserDB, ScanHistoryDB, ScanHistoryCreateSchema, PlagiarismResultSchema
from backend.tests.test_db_setup import TestingSessionLocal, init_test_db
from backend.routers.auth import get_password_hash # For creating a test user

class TestHistoryCrud(unittest.TestCase):

    def setUp(self):
        # Initialize a clean database for each test or test suite
        init_test_db()
        self.db: Session = next(TestingSessionLocal()) # Get a session

        # Create a test user
        self.test_user_email = "historyuser@example.com"
        self.test_user_password = "testpassword"
        hashed_password = get_password_hash(self.test_user_password)
        self.user = UserDB(email=self.test_user_email, hashed_password=hashed_password, is_active=True)
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.close()
        # init_test_db() # Optionally re-initialize to drop tables after tests too

    def test_create_and_read_scan_history(self):
        # 1. Create a ScanHistory entry
        scan_result_data = PlagiarismResultSchema(
            originality_score=0.85,
            matched_sources=["Source A", "Source B"],
            rewrite_suggestions=["Suggestion 1"]
        )

        history_entry_in = ScanHistoryCreateSchema(
            content_type="text_input",
            file_name=None,
            input_snippet="This is a test snippet for history.",
            originality_score=scan_result_data.originality_score,
            matched_sources=scan_result_data.matched_sources,
            rewrite_suggestions=scan_result_data.rewrite_suggestions
        )

        db_history_entry = ScanHistoryDB(
            user_id=self.user.id,
            content_type=history_entry_in.content_type,
            file_name=history_entry_in.file_name,
            input_snippet=history_entry_in.input_snippet,
            originality_score=history_entry_in.originality_score,
            matched_sources_json=json.dumps(history_entry_in.matched_sources),
            rewrite_suggestions_json=json.dumps(history_entry_in.rewrite_suggestions)
        )
        self.db.add(db_history_entry)
        self.db.commit()
        self.db.refresh(db_history_entry)

        self.assertIsNotNone(db_history_entry.id)
        self.assertEqual(db_history_entry.user_id, self.user.id)
        self.assertEqual(db_history_entry.input_snippet, "This is a test snippet for history.")

        # 2. Read ScanHistory entries for the user
        retrieved_history = (
            self.db.query(ScanHistoryDB)
            .filter(ScanHistoryDB.user_id == self.user.id)
            .order_by(ScanHistoryDB.timestamp.desc())
            .all()
        )

        self.assertEqual(len(retrieved_history), 1)
        first_entry = retrieved_history[0]
        self.assertEqual(first_entry.id, db_history_entry.id)
        self.assertEqual(first_entry.content_type, "text_input")
        self.assertEqual(first_entry.originality_score, 0.85)

        # Check JSON fields
        self.assertEqual(json.loads(first_entry.matched_sources_json), ["Source A", "Source B"])
        self.assertEqual(json.loads(first_entry.rewrite_suggestions_json), ["Suggestion 1"])

    def test_multiple_history_entries(self):
        # Entry 1
        history_data_1 = ScanHistoryCreateSchema(
            content_type="file_pdf", file_name="report.pdf", input_snippet="PDF report content",
            originality_score=0.95, matched_sources=[], rewrite_suggestions=[]
        )
        db_entry_1 = ScanHistoryDB(user_id=self.user.id, **history_data_1.model_dump(exclude_unset=True),
                                   matched_sources_json=json.dumps(history_data_1.matched_sources),
                                   rewrite_suggestions_json=json.dumps(history_data_1.rewrite_suggestions))
        self.db.add(db_entry_1)

        # Entry 2
        history_data_2 = ScanHistoryCreateSchema(
            content_type="image_png", file_name="logo.png", input_snippet="Image scan",
            originality_score=0.50, matched_sources=["Mock Source 1"], rewrite_suggestions=["Use original image"]
        )
        db_entry_2 = ScanHistoryDB(user_id=self.user.id, **history_data_2.model_dump(exclude_unset=True),
                                   matched_sources_json=json.dumps(history_data_2.matched_sources),
                                   rewrite_suggestions_json=json.dumps(history_data_2.rewrite_suggestions))
        self.db.add(db_entry_2)

        self.db.commit()

        retrieved_history = (
            self.db.query(ScanHistoryDB)
            .filter(ScanHistoryDB.user_id == self.user.id)
            .order_by(ScanHistoryDB.timestamp.asc()) # Ascending for predictable order
            .all()
        )
        self.assertEqual(len(retrieved_history), 2)
        self.assertEqual(retrieved_history[0].content_type, "file_pdf")
        self.assertEqual(retrieved_history[1].content_type, "image_png")
        self.assertEqual(json.loads(retrieved_history[1].rewrite_suggestions_json), ["Use original image"])


if __name__ == '__main__':
    # Ensure test DB is initialized before running tests if module is run directly
    # init_test_db() # This might be better in a global setup for the test runner
    unittest.main()
