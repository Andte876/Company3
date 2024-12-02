# Routes
from flask_jwt_extended import jwt_required
from flask import Blueprint
from .cameras_controller import CameraController

cameras_bp = Blueprint("cameras", __name__)


@cameras_bp.route("/", methods=["GET"])
def get_cameras():
    return CameraController.get_cameras()


@cameras_bp.route("/add", methods=["POST"])
def add_camera():
    return CameraController.add_camera()


@cameras_bp.route("/locations", methods=["GET"])
def locations():
    return CameraController.locations()


@cameras_bp.route("/locations/<string:location>", methods=["GET"])
def cameraID_by_location(location):
    return CameraController.cameraID_by_location(location)


@cameras_bp.route("/<string:camera_id>/confidence", methods=["GET"])
def get_confidence_threshold(camera_id):
    return CameraController.get_confidence_threshold(camera_id)


@cameras_bp.route("/<string:camera_id>", methods=["GET"])
def get_camera_by_id(camera_id):
    return CameraController.get_camera(camera_id)


@cameras_bp.route("/<string:camera_id>/conf/<string:confidence>", methods=["POST"])
def set_confidence(camera_id, confidence):
    return CameraController.set_confidence(camera_id, confidence)


@cameras_bp.route("/<string:camera_id>", methods=["DELETE"])
def delete_camera_by_id(camera_id):
    return CameraController.delete_camera(camera_id)


@cameras_bp.route("/<string:camera_id>/confidence", methods=["PUT"])
@jwt_required()
def update_confidence(camera_id):
    return CameraController.update_confidence(camera_id)


@cameras_bp.route("/<string:camera_id>/location", methods=["PUT"])
def update_location(camera_id):
    return CameraController.update_location(camera_id)


@cameras_bp.route("/upload/data", methods=["POST"])
def process_camera_data():
    return CameraController.process_camera_data()


@cameras_bp.route("/<string:camera_id>/ip", methods=["PUT"])
def update_ip(camera_id):
    return CameraController.update_ip(camera_id)


# Routes
@cameras_bp.route("/<string:camera_id>/schedule", methods=["PUT"])
def update_schedule(camera_id):
    return CameraController.update_schedule(camera_id)
