"""
Email service for handling IMAP operations.

This service encapsulates all email-related functionality, providing a consistent
interface for operations like fetching emails, moving emails between folders,
and listing folders.
"""

import ssl
from typing import List, Optional, Any, Callable, TypeVar, Dict

from imap_tools import MailBox, A, MailMessage, Header
from veloxforce_tools.core.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")  # Type variable for return type of operations


class EmailService:
    """
    Service for email operations using IMAP.

    This service encapsulates all email-related functionality, providing a consistent
    interface for operations like fetching emails, moving emails between folders,
    and listing folders.
    """

    def __init__(
        self, imap_server: str, email_address: str, password: str, folder: str = "INBOX"
    ):
        """Initialize the EmailService.

        Args:
            imap_server: IMAP server address
            email_address: Email address for login
            password: Password for login
            folder: Default folder to use
        """
        self.imap_server = imap_server
        self.email_address = email_address
        self.password = password
        self.folder = folder

    def _create_mailbox(self) -> MailBox:
        """Create a MailBox instance with proper SSL context.

        Returns:
            A configured MailBox instance
        """
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        return MailBox(self.imap_server, ssl_context=context)

    async def execute_with_mailbox(self, operation_func: Callable[[MailBox], T]) -> T:
        """Execute an operation with a mailbox and handle cleanup.

        Args:
            operation_func: Function that takes a MailBox and returns a result

        Returns:
            The result of the operation

        Raises:
            Exception: If the operation fails
        """
        mailbox = None
        try:
            mailbox = self._create_mailbox()
            mailbox.login(self.email_address, self.password, self.folder)
            return operation_func(mailbox)
        except Exception as e:
            logger.error(f"Error executing mailbox operation: {e}", exc_info=True)
            raise
        finally:
            if mailbox and mailbox.client:
                try:
                    mailbox.logout()
                except Exception as e:
                    logger.debug(f"Error during IMAP logout (can be ignored): {e}")

    async def fetch_emails_by_ids(self, email_ids: List[str]) -> List[MailMessage]:
        """Fetch emails by their IDs.

        Args:
            email_ids: List of email IDs to fetch

        Returns:
            List of MailMessage objects
        """
        if not email_ids:
            return []

        logger.info(f"Fetching {len(email_ids)} emails by ID")

        def _operation(mailbox: MailBox) -> List[MailMessage]:
            uid_criteria = ",".join(email_ids)
            messages = list(mailbox.fetch(A(uid=uid_criteria)))
            logger.info(f"Successfully fetched {len(messages)} emails")
            return messages

        try:
            return await self.execute_with_mailbox(_operation)
        except Exception as e:
            logger.error(f"Error fetching emails by ID: {e}", exc_info=True)
            return []

    async def fetch_emails_by_message_ids(
        self, message_ids: List[str]
    ) -> List[MailMessage]:
        """Fetch emails by their Message-ID headers.

        Args:
            message_ids: List of message IDs to fetch (with or without angle brackets)

        Returns:
            List of MailMessage objects
        """
        if not message_ids:
            return []

        logger.info(f"Fetching {len(message_ids)} emails by Message-ID")

        def _operation(mailbox: MailBox) -> List[MailMessage]:
            messages = []

            for message_id in message_ids:
                # Ensure message ID has angle brackets for proper IMAP search
                formatted_message_id = (
                    message_id if message_id.startswith("<") else f"<{message_id}>"
                )
                if not formatted_message_id.endswith(">"):
                    formatted_message_id += ">"

                logger.debug(f"Searching for message ID: {formatted_message_id}")

                # Search for emails with this specific message ID using Header class
                try:
                    found_messages = list(
                        mailbox.fetch(
                            A(header=Header("Message-ID", formatted_message_id))
                        )
                    )
                    if found_messages:
                        messages.extend(found_messages)
                        logger.debug(
                            f"Found {len(found_messages)} email(s) for message ID {formatted_message_id}"
                        )
                    else:
                        logger.warning(
                            f"No email found for message ID: {formatted_message_id}"
                        )
                except Exception as e:
                    logger.error(
                        f"Error searching for message ID {formatted_message_id}: {e}"
                    )
                    continue

            logger.info(f"Successfully fetched {len(messages)} emails by Message-ID")
            return messages

        try:
            return await self.execute_with_mailbox(_operation)
        except Exception as e:
            logger.error(f"Error fetching emails by Message-ID: {e}", exc_info=True)
            return []

    async def move_email_to_folder(self, email_id: str, target_folder: str) -> bool:
        """Move an email to a different folder.

        Args:
            email_id: The UID of the email to move
            target_folder: The name of the target folder

        Returns:
            True if the move was successful, False otherwise
        """
        logger.info(f"Moving email {email_id} to folder '{target_folder}'")

        def _operation(mailbox: MailBox) -> bool:
            # Check if target folder exists
            folders = list(mailbox.folder.list())
            folder_names = [f.name for f in folders]

            if target_folder not in folder_names:
                logger.warning(f"Target folder '{target_folder}' does not exist")
                # Create the folder if it doesn't exist
                logger.info(f"Creating folder '{target_folder}'")
                mailbox.folder.create(target_folder)

            # Move the email to the target folder
            mailbox.move(email_id, target_folder)
            logger.info(
                f"Successfully moved email {email_id} to folder '{target_folder}'"
            )
            return True

        try:
            return await self.execute_with_mailbox(_operation)
        except Exception as e:
            logger.error(
                f"Error moving email {email_id} to folder '{target_folder}': {e}",
                exc_info=True,
            )
            return False

    async def list_folders(self) -> List[str]:
        """List all available folders in the mailbox.

        Returns:
            List of folder names
        """
        logger.info("Listing available folders")

        def _operation(mailbox: MailBox) -> List[str]:
            folders = list(mailbox.folder.list())
            folder_names = [f.name for f in folders]
            logger.info(f"Available folders: {folder_names}")
            return folder_names

        try:
            return await self.execute_with_mailbox(_operation)
        except Exception as e:
            logger.error(f"Error listing folders: {e}", exc_info=True)
            return []
