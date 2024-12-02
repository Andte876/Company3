# This file contains the controller for the alarms module
from flask import request, jsonify
from app.models import Alarm  # important for frontend
from .alarms_service import AlarmService
from app.socketio_instance import socketio


class AlarmController:
    def get_alarms():
        return jsonify(AlarmService.get_alarms()), 200

    def get_active_alarms(type):
        return jsonify(AlarmService.get_active_alarms(type)), 200

    @staticmethod
    def add_alarm():
        alarm_data = request.get_json()
        print(alarm_data)  # Debugging
        new_alarm = AlarmService.create_alarm(alarm_data)
        if new_alarm["status"] == "success":
            # Notify frontend about the new alarm
            socketio.emit("new_alarm", new_alarm["alarm"])
            return jsonify(new_alarm), 201
        else:
            return jsonify({"message": new_alarm["message"]}), 400

    def get_alarm_image(alarm_ID):
        return AlarmService.get_alarm_image(alarm_ID)

    def get_alarm_by_operator(operator):
        return AlarmService.get_alarm_by_operator(operator)

    def get_alarm_by_camera(location, camera_ID):
        return AlarmService.get_alarm_by_camera(location, camera_ID)

    # Properly serializes the Alarm object using to_dict() to ensure correct JSON formatting for frontend compatibility
    @staticmethod
    def get_alarm_by_id(alarm_id):
        # Fetch the alarm from the database by ID
        alarm = Alarm.query.get(alarm_id)
        if alarm:
            # Convert to dictionary and return as JSON
            return jsonify(alarm.to_dict())
        else:
            return jsonify({"error": "Alarm not found"}), 404

    def delete_alarm_by_id(alarm_id):
        return AlarmService.delete_alarm_by_id(alarm_id)

    def notify_guard(guard_ID, alarm_ID):
        return AlarmService.notify_guard(guard_ID, alarm_ID)

    def update_alarm_status(alarm_id):
        alarm_data = request.get_json()
        if not alarm_data or "status" not in alarm_data:
            return jsonify({"message": "Status is required"}), 400

        # Get guard_id from the request data
        guard_id = alarm_data.get("guard_id")
        operator_id = alarm_data.get(
            "operator_id"
        )  # Get operator_id from the request data
        updated_alarm = AlarmService.update_alarm_status(
            alarm_id, alarm_data["status"], guard_id, operator_id
        )
        if updated_alarm:
            return jsonify(updated_alarm), 200
        else:
            return jsonify(
                {"message": "Alarm not found or invalid guard/operator ID"}
            ), 404
