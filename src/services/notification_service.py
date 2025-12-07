"""Notification service - Application logic layer for push notifications."""
from typing import List, Optional
import os
from src.utils.logger import get_logger

# Firebase Admin SDK imports
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    get_logger(__name__).warning("firebase-admin not installed. Push notifications disabled.")


class NotificationService:
    """Service for handling push notifications via Firebase Cloud Messaging."""
    
    def __init__(self):
        """Initialize the notification service."""
        self.logger = get_logger(__name__)
        self._initialized = False
        self._initialize_firebase()
        self.logger.info("NotificationService initialized successfully")
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        if not FIREBASE_AVAILABLE:
            self.logger.warning("Firebase Admin SDK not available. Notifications disabled.")
            return
        
        if self._initialized:
            return
        
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
            self._initialized = True
            self.logger.info("Firebase Admin already initialized")
            return
        except ValueError:
            # Firebase not initialized yet
            pass
        
        try:
            # Try to load service account key from config directory
            cred_path = os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'config', 'firebase-service-account.json'
            )
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self._initialized = True
                self.logger.info("Firebase Admin initialized with service account key")
            else:
                # Try environment variable (for production)
                if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                    firebase_admin.initialize_app()
                    self._initialized = True
                    self.logger.info("Firebase Admin initialized with default credentials")
                else:
                    self.logger.warning(
                        f"Firebase service account key not found at {cred_path}. "
                        "Notifications will be disabled. Set GOOGLE_APPLICATION_CREDENTIALS "
                        "environment variable or place key file at config/firebase-service-account.json"
                    )
        except Exception as e:
            self.logger.error(f"Error initializing Firebase: {e}")
            self._initialized = False
    
    async def send_group_chat_notification(
        self,
        group_id: str,
        group_name: str,
        sender_username: str,
        message: str,
        recipient_user_ids: List[str],
        fcm_tokens: dict[str, str]
    ) -> bool:
        """
        Send notification to all group members when a new chat message is posted.
        
        Args:
            group_id: ID of the group
            group_name: Name of the group
            sender_username: Username of the message sender
            message: The chat message content
            recipient_user_ids: List of user IDs to notify (excluding sender)
            fcm_tokens: Dictionary mapping user_id to fcm_token
        
        Returns:
            bool: True if notifications were sent successfully
        """
        if not self._initialized or not FIREBASE_AVAILABLE:
            self.logger.debug("Firebase not initialized, skipping notification")
            return False
        
        if not recipient_user_ids:
            self.logger.debug("No recipients for notification")
            return True
        
        # Filter out users without FCM tokens
        tokens_to_notify = [
            fcm_tokens.get(user_id) 
            for user_id in recipient_user_ids 
            if fcm_tokens.get(user_id)
        ]
        
        if not tokens_to_notify:
            self.logger.debug("No FCM tokens available for recipients")
            return True
        
        try:
            self.logger.debug(f"Sending notifications to {len(tokens_to_notify)} devices")
            
            # Truncate message if too long
            message_preview = message[:100] + "..." if len(message) > 100 else message
            
            # Create notification message
            notification = messaging.Notification(
                title=f"New message in {group_name}",
                body=f"{sender_username}: {message_preview}",
            )
            
            # Create data payload for deep linking
            data = {
                'type': 'group_chat',
                'groupId': group_id,
                'senderUsername': sender_username,
            }
            
            # Create multicast message
            message_obj = messaging.MulticastMessage(
                notification=notification,
                data=data,
                tokens=tokens_to_notify,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        channel_id='group_chat_channel',
                        sound='default',
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                        ),
                    ),
                ),
            )
            
            # Send notifications
            response = messaging.send_multicast(message_obj)
            
            # Log results
            if response.failure_count > 0:
                self.logger.warning(f"Failed to send {response.failure_count} notifications")
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        self.logger.debug(f"Failure {idx}: {resp.exception}")
            
            if response.success_count > 0:
                self.logger.info(f"Successfully sent {response.success_count} notifications")
            
            return response.success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}", exc_info=True)
            return False


