# This file contains the service layer for the alarms module

from app.models import Alarm, AlarmStatus, User, UserRole, Camera
from typing import List
from flask import jsonify
from sqlalchemy import desc
from app.extensions import db  # Import the database instance

# To send email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config
import base64
from email.mime.image import MIMEImage


class AlarmService:
    @staticmethod
    def get_alarms() -> List[dict]:
        alarms = (
            db.session.query(Alarm, Camera.location)
            .join(Camera, Camera.id == Alarm.camera_id)
            .all()
        )
        return [{**alarm.to_dict(), "location": location} for alarm, location in alarms]

    def get_active_alarms(alarm_type: str) -> List[dict]:
        if alarm_type.lower() == "new":
            # Get all alarms with status 'PENDING' or 'NOTIFIED'
            alarms = Alarm.query.filter(
                Alarm.status.in_([AlarmStatus.PENDING, AlarmStatus.NOTIFIED])
            ).all()
        elif alarm_type.lower() == "old":
            # Get the 10 most recent alarms with status 'RESOLVED' or 'IGNORED'
            alarms = (
                Alarm.query.filter(
                    Alarm.status.in_([AlarmStatus.RESOLVED, AlarmStatus.IGNORED])
                )
                .order_by(desc(Alarm.timestamp))
                .limit(10)
                .all()
            )
        else:
            # Default case if `alarm_type` doesn't match 'new' or 'old'
            alarms = []

        return [alarm.to_dict() for alarm in alarms]

    @staticmethod
    def get_alarm_by_camera(location: str, camera_id: str) -> List[dict]:
        alarms = (
            db.session.query(Alarm)
            .join(Camera, Camera.id == Alarm.camera_id)
            .filter(Camera.location == location, Alarm.camera_id == camera_id)
            .all()
        )
        return [alarm.to_dict() for alarm in alarms]

    @staticmethod
    def get_alarm_by_operator(operator) -> List[dict]:
        alarms = db.session.query(Alarm).filter(Alarm.operator_id == operator).all()
        return [alarm.to_dict() for alarm in alarms]

    @staticmethod
    def create_alarm(alarm_data):
        # Step 1: Extract the alarm data
        camera_id = alarm_data.get("camera_id")
        confidence_score = alarm_data.get("confidence_score")
        alarm_type = alarm_data.get("type")
        image_base64 = alarm_data.get("image_base64")

        # Step 2: Check if camera_id exists in the database
        camera = Camera.query.filter_by(id=camera_id).first()
        if not camera:
            return {"status": "error", "message": "Camera not found"}

        # Step 3: Check if there is any active alarm with status PENDING or NOTIFIED for the given camera_id
        active_alarm = Alarm.query.filter(
            Alarm.camera_id == camera_id,
            Alarm.status.in_([AlarmStatus.PENDING, AlarmStatus.NOTIFIED]),
        ).first()
        if active_alarm:
            return {
                "status": "error",
                "message": "Already alarm active: " + str(active_alarm.status.value),
            }

        # Step 4: Check if confidence_score meets the threshold
        if confidence_score < camera.confidence_threshold:
            return {"status": "error", "message": "Confidence score below threshold"}

        # Step 5: Create a new alarm
        new_alarm = Alarm(
            camera_id=camera_id,
            type=alarm_type,
            confidence_score=confidence_score,
            image_base64=image_base64,
            status=AlarmStatus.PENDING,
        )
        db.session.add(new_alarm)
        db.session.commit()

        # Step 5: get the location
        camera = Camera.query.filter_by(id=camera_id).first()
        if not camera:
            return {"status": "error", "message": "Camera not found"}

        return {
            "status": "success",
            "alarm": new_alarm.to_dict(),
            "camera_location": camera.location,
        }

    def get_alarm_by_id(schedule_id):
        return  # add logic

    def get_alarm_image(alarm_ID):
        # Retrieve the alarm by ID
        alarm = Alarm.query.filter_by(id=alarm_ID).first()
        if not alarm:
            return jsonify({"status": "No alarm found"}), 404

        # Retrieve the associated image snapshot
        image_base64 = alarm.image_base64
        if not image_base64:
            return jsonify({"status": "No image snapshot associated with alarm"}), 404

        # Decode and return the image data
        try:
            # image_data = base64.b64decode(image_base64)
            # Return the Base64 directly
            return jsonify({"image": image_base64}), 200
        except Exception as e:
            print(f"Failed to decode image. Error: {e}")
            return jsonify({"status": "Failed to decode image"}), 500

    def update_alarm_status(alarm_id, new_status, guard_id=None, operator_id=None):
        # Find the alarm by ID
        alarm = Alarm.query.get(alarm_id)
        if alarm:
            # Check if the status is valid
            if new_status not in [status.value for status in AlarmStatus]:
                return None  # Invalid status

            # Update the alarm status by converting the string to an AlarmStatus enum
            alarm.status = AlarmStatus[new_status.upper()]

            # If the status is changed to IGNORED, delete the image attribute
            if new_status.upper() == "IGNORED":
                alarm.image_base64 = None

            # If the status is "notified", update the guard_id
            if new_status.upper() == "NOTIFIED" and guard_id:
                guard = User.query.filter_by(id=guard_id, role=UserRole.GUARD).first()
                if guard:
                    alarm.guard_id = guard_id
                else:
                    return None  # Invalid guard_id

            # Update the operator_id if provided
            if operator_id:
                operator = User.query.filter_by(
                    id=operator_id, role=UserRole.OPERATOR
                ).first()
                if operator:
                    alarm.operator_id = operator_id
                else:
                    return None  # Invalid operator_id

            # Commit the changes to the database
            db.session.commit()
            return alarm.to_dict()  # Return the updated alarm as a dictionary
        return None  # Alarm not found

    def delete_alarm_by_id(schedule_id):
        #    alarm = AlarmController.get_alarm_by_id(alarm_id)
        #    if alarm:
        #        return jsonify(alarm)
        #    else:
        #        return jsonify({"message": "Alarm not found"})
        #        return jsonify({"alarm_id": str(alarm_id)})
        return  # add logic

    def notify_guard(guard_ID, alarm_ID):
        # Step 1: Get the guard's email
        guard = User.query.filter_by(id=guard_ID, role="GUARD").first()
        if not guard:
            return jsonify({"status": "No guard found"}), 404

        # Step 2: Get the image URL from the alarm
        alarm = Alarm.query.filter_by(id=alarm_ID).first()
        if not alarm:
            return jsonify({"status": "No alarm found"}), 404

        # Retrieve the associated image snapshot URL
        image_base64 = alarm.image_base64
        if not image_base64:
            return jsonify({"status": "No image snapshot associated with alarm"}), 404

        # Step 3: Send the email
        score = alarm.confidence_score
        subject = "Human Detected Alert"
        body = f"Slow down cowboy! \nYou have been caught with a score: {score}\n Please check the image attached.\n Head to camera id: {alarm.camera_id}"
        to_email = guard.email
        # Gmail account credentials
        from_email = "tddc88.company3@gmail.com"
        from_password = Config.email_pswrd

        # Create the email
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            image_data = base64.b64decode(image_base64)
            image_attachment = MIMEImage(image_data, name="alarm_image.jpeg")
            msg.attach(image_attachment)
        except Exception as e:
            print(f"Failed to decode image. Error: {e}")
            return jsonify({"status": "Failed to decode image"}), 500

        try:
            print("Email content before sending:")
            print(msg)
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(from_email, from_password)
            content = msg.as_string()
            print(content)
            server.sendmail(from_email, to_email, content)
            server.quit()

            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email. Error: {e}")

        # Step 4: Update the alarm status to confirmed
        alarm.status = AlarmStatus.NOTIFIED
        db.session.commit()

        # Step 5: Placeholder for sending the notification
        # print(f"Sending notification to {guard.email} with alarm image URL: {image_snapshot.url}")
        return "success"
