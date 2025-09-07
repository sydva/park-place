import base64
import os
from pathlib import Path
from typing import Any

import anthropic


class VerificationResult:
    def __init__(
        self,
        is_verified: bool,
        license_plate_match: bool = False,
        name_match: bool = False,
        valid_drivers_license: bool = False,
        valid_registration: bool = False,
        photo_match: bool = False,
        details: str = "",
    ):
        self.is_verified = is_verified
        self.license_plate_match = license_plate_match
        self.name_match = name_match
        self.valid_drivers_license = valid_drivers_license
        self.valid_registration = valid_registration
        self.photo_match = photo_match
        self.details = details


class DocumentVerificationService:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _get_media_type(self, file_path: str) -> str:
        """Get media type based on file extension"""
        ext = Path(file_path).suffix.lower()
        if ext in [".jpg", ".jpeg"]:
            return "image/jpeg"
        elif ext == ".png":
            return "image/png"
        elif ext == ".pdf":
            return "application/pdf"
        else:
            return "image/jpeg"  # Default fallback

    async def verify_documents(
        self,
        profile_photo_path: str,
        id_document_path: str,
        vehicle_registration_path: str,
        entered_license_plate: str,
    ) -> VerificationResult:
        """
        Verify identity documents using Claude AI
        
        Args:
            profile_photo_path: Path to the profile photo
            id_document_path: Path to the driver's license
            vehicle_registration_path: Path to the vehicle registration
            entered_license_plate: The license plate the user entered
        
        Returns:
            VerificationResult with verification details
        """
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("Warning: ANTHROPIC_API_KEY not set. Skipping AI verification.")
            return VerificationResult(
                is_verified=False,
                details="AI verification service not configured"
            )

        try:
            # Encode all images
            profile_photo_b64 = self._encode_image(profile_photo_path)
            id_document_b64 = self._encode_image(id_document_path)
            vehicle_registration_b64 = self._encode_image(vehicle_registration_path)

            # Create the verification prompt
            prompt = f"""I need you to analyze these identity verification documents and check 5 specific criteria. Please examine all three images carefully:

1. Profile Photo - A selfie of the person
2. Driver's License - US driver's license document  
3. Vehicle Registration - US vehicle registration document

The user entered this license plate number: "{entered_license_plate}"

Please verify these 5 points and respond ONLY with a JSON object in this exact format:

{{
    "license_plate_match": true/false,
    "name_match": true/false, 
    "valid_drivers_license": true/false,
    "valid_registration": true/false,
    "photo_match": true/false,
    "details": "Detailed explanation of your findings"
}}

Verification Criteria:
1. license_plate_match: Does the license plate on the vehicle registration exactly match "{entered_license_plate}"?
2. name_match: Does the name on the vehicle registration match the name on the driver's license?  
3. valid_drivers_license: Does the driver's license appear to be a valid US driver's license (not expired, proper format, clear photo)?
4. valid_registration: Does the vehicle registration appear to be a valid US vehicle registration document?
5. photo_match: Does the person in the profile photo appear to be the same person as in the driver's license photo?

Be strict in your verification - only return true if you are confident the criteria is met. If any document is unclear, blurry, or suspicious, mark the relevant criteria as false."""

            # Make API call to Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": self._get_media_type(profile_photo_path),
                                    "data": profile_photo_b64
                                }
                            },
                            {
                                "type": "image", 
                                "source": {
                                    "type": "base64",
                                    "media_type": self._get_media_type(id_document_path),
                                    "data": id_document_b64
                                }
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64", 
                                    "media_type": self._get_media_type(vehicle_registration_path),
                                    "data": vehicle_registration_b64
                                }
                            }
                        ]
                    }
                ]
            )

            # Parse response
            response_text = message.content[0].text.strip()
            print(f"Claude verification response: {response_text}")

            # Parse JSON response
            import json
            try:
                result_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response if it's wrapped in other text
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result_data = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from Claude response")

            # All 5 criteria must be true for verification to pass
            all_verified = all([
                result_data.get("license_plate_match", False),
                result_data.get("name_match", False),
                result_data.get("valid_drivers_license", False),
                result_data.get("valid_registration", False),
                result_data.get("photo_match", False)
            ])

            return VerificationResult(
                is_verified=all_verified,
                license_plate_match=result_data.get("license_plate_match", False),
                name_match=result_data.get("name_match", False),
                valid_drivers_license=result_data.get("valid_drivers_license", False),
                valid_registration=result_data.get("valid_registration", False),
                photo_match=result_data.get("photo_match", False),
                details=result_data.get("details", "")
            )

        except Exception as e:
            print(f"Error during document verification: {e}")
            return VerificationResult(
                is_verified=False,
                details=f"Verification failed due to error: {str(e)}"
            )