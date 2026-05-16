import os
import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore, storage

logger = logging.getLogger(__name__)



class FirebaseConfig:
    """Manages Firebase service initialization and provides access to clients."""

    _firestore_client: Optional[firestore.Client] = None
    _storage_bucket = None

    @classmethod
    def initialize(cls) -> None:
        """
        Initialize Firebase Admin SDK with credentials from service account JSON file.

        Expected workflow:
        1. Download Firebase service account JSON from Firebase Console
           > Project Settings > Service Accounts > Generate new private key
        2. Save the file as: backend/app/config/firebase-key.json
        3. This file should be added to .gitignore (never commit credentials!)
        4. When running locally, ensure FIREBASE_CREDENTIALS_PATH env var is set

        Raises:
            FileNotFoundError: If credentials file is not found
            ValueError: If Firebase app is already initialized
        """
        try:
            # Get credentials path from environment or use default
            # Default to the firebase-key.json located next to this config file
            default_cred_path = os.path.join(os.path.dirname(__file__), "firebase-key.json")

            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", default_cred_path)

            # Normalize path for cross-platform compatibility
            cred_path = os.path.normpath(cred_path)

            # Check if file exists
            if not os.path.exists(cred_path):
                logger.warning(
                    f"Firebase credentials file not found at {cred_path}. "
                    "Please download your service account JSON from Firebase Console "
                    "and save it at the path specified in FIREBASE_CREDENTIALS_PATH environment variable. "
                    "Running without Firebase will result in errors when accessing the database."
                )
                raise FileNotFoundError(
                    f"Firebase credentials file not found: {cred_path}"
                )

            # Initialize Firebase if not already done
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")
            else:
                logger.info("Firebase Admin SDK already initialized")

            # Initialize Firestore and Storage clients
            cls._firestore_client = firestore.client()
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")

            if storage_bucket:
                cls._storage_bucket = storage.bucket(storage_bucket)
                logger.info(f"Firebase Storage bucket initialized: {storage_bucket}")
            else:
                logger.warning(
                    "FIREBASE_STORAGE_BUCKET not set. "
                    "Image uploads to Storage will not work until this is configured."
                )

        except FileNotFoundError as e:
            logger.error(f"Firebase initialization failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Firebase initialization: {e}")
            raise

    @classmethod
    def get_firestore_client(cls) -> firestore.Client:
        """
        Get Firestore client instance.

        Returns:
            firestore.Client: Initialized Firestore client

        Raises:
            RuntimeError: If Firebase has not been initialized
        """
        if cls._firestore_client is None:
            logger.error("Firestore client not initialized. Call FirebaseConfig.initialize() first.")
            raise RuntimeError("Firebase has not been initialized. Call FirebaseConfig.initialize() first.")
        return cls._firestore_client

    @classmethod
    def get_storage_bucket(cls):
        """
        Get Firebase Storage bucket instance.

        Returns:
            storage.Bucket: Initialized Storage bucket or None if not configured

        Raises:
            RuntimeError: If Firebase has not been initialized
        """
        if cls._firestore_client is None:
            logger.error("Firebase not initialized. Call FirebaseConfig.initialize() first.")
            raise RuntimeError("Firebase has not been initialized. Call FirebaseConfig.initialize() first.")

        if cls._storage_bucket is None:
            logger.warning(
                "Storage bucket not available. "
                "Ensure FIREBASE_STORAGE_BUCKET environment variable is set."
            )

        return cls._storage_bucket


# Initialize Firebase on module import (production pattern)
try:
    FirebaseConfig.initialize()
except Exception as e:
    logger.warning(f"Firebase initialization skipped (may be running in test/dev mode): {e}")
