import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import Header from "../components/OperatorHeader";
import { baseURL } from "../api/axiosConfig";

const AlarmDetailPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [alarm, setAlarm] = useState(null);
  const [liveFootage, setLiveFootage] = useState(""); // State for live footage image
  const [notificationMessage, setNotificationMessage] = useState("");
  const [notificationType, setNotificationType] = useState("");
  const [users, setUsers] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [manualNotifyVisible, setManualNotifyVisible] = useState(false);
  const [callChecked, setCallChecked] = useState(false);

  const id = location.state?.id || sessionStorage.getItem("alarmId");

  useEffect(() => {
    if (!id) {
      setNotificationMessage("Alarm ID is missing.");
      setNotificationType("error");
      navigate("/alert-details");
      return;
    }

    sessionStorage.removeItem("alarmData");

    const fetchAlarmDetails = async () => {
      try {
        const response = await axios.get(`${baseURL}/alarms/${id}`);
        const alarmData = response.data;
        setAlarm({
          id: alarmData.id || alarmData.alarm_id,
          camera_id: alarmData.camera_id || "N/A",
          type: alarmData.type || "N/A",
          confidence_score: alarmData.confidence_score || 0,
          timestamp: alarmData.timestamp || "N/A",
          operator_id: alarmData.operator_id || "N/A",
          status: alarmData.status || "N/A",
        });
      } catch (err) {
        setNotificationMessage(
          err.response && err.response.status === 404
            ? "Alarm not found."
            : "Failed to load alarm details.",
        );
        setNotificationType("error");
      }
    };

    const fetchAlarmImage = async () => {
      try {
        const imageResponse = await axios.get(`${baseURL}/alarms/${id}/image`);
        if (imageResponse.data && imageResponse.data.image) {
          // Update liveFootage with Base64 image data URL
          setLiveFootage(`data:image/jpeg;base64,${imageResponse.data.image}`);
        }
      } catch (error) {
        console.error("Error fetching image:", error);
        setNotificationMessage("Failed to load alarm image.");
        setNotificationType("error");
      }
    };

    const fetchUsers = async () => {
      try {
        const response = await axios.get(`${baseURL}/users/guards`);
        setUsers(response.data);
      } catch (err) {
        console.error("Error fetching guards:", err);
        setNotificationMessage("Failed to load guards.");
        setNotificationType("error");
      }
    };

    // Call all functions when component loads
    fetchAlarmDetails();
    fetchAlarmImage();
    fetchUsers();
  }, [id, navigate]);

  useEffect(() => {
    if (location.state?.notifyFailed) {
      setNotificationMessage(
        "Notification failed. Call the guard and confirm manual handling.",
      );
      setNotificationType("error");
      setManualNotifyVisible(true);
    }
  }, [location.state]);

  const updateAlarmStatus = async (newStatus, guardID = null) => {
    if (newStatus === "resolved") {
      const confirmResolve = window.confirm(
        "Are you sure you want to resolve the alarm?",
      );
      if (!confirmResolve) {
        return; // Exit if user cancels the confirmation
      }
    }

    try {
      const response = await axios.put(`${baseURL}/alarms/${id}/status`, {
        status: newStatus,
        guard_id: guardID, // Include guard_id in the request payload
        // TODO: send operator_id in the request payload based on the inlogged user
      });
      setAlarm((prevAlarm) => ({
        ...prevAlarm,
        status: response.data.status,
      }));

      if (newStatus === "ignored") {
        window.alert("Alarm dismissed successfully.");
        navigate("/operator"); // Navigate back to the operator page after confirmation
      }

      if (newStatus === "notified") {
        window.alert("Alarm status updated to notified");
        navigate("/operator"); // Navigate back to the operator page after confirmation
      }

      if (newStatus === "resolved") {
        window.alert("Alarm status updated to resolved");
        navigate("/operator"); // Navigate back to the operator page after resolving
      }
    } catch (err) {
      console.error("Error updating alarm status:", err);
      setNotificationMessage(`Failed to update status to ${newStatus}.`);
      setNotificationType("error");
    }
  };

  const notifyGuard = async (guardID) => {
    const username = "root"; // Replace with your username
    const password = "secure"; // Replace with your password
    const auth = "Basic " + btoa(`${username}:${password}`);

    try {
      const response = await axios.post(
        `${baseURL}/alarms/notify/${guardID}/${id}`,
        {},
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: auth,
          },
        },
      );

      const guardName =
        users.find((user) => user.id === guardID)?.username || "the guard";
      console.log(`Guard ${guardName} notified successfully:`, response.data);
      setNotificationMessage(`Notification sent to ${guardName}.`);
      setNotificationType("success");
      setManualNotifyVisible(false);
      return true; // Notification succeeded
    } catch (err) {
      console.error(
        "Error notifying the guard:",
        err.response ? err.response.data : err.message,
      );
      setNotificationMessage("Failed to notify the guard.");
      setNotificationType("error");
      setManualNotifyVisible(true);
      return false; // Notification failed
    }
  };

  const handleNotifyAndUpdate = async () => {
    if (!selectedUserId) {
      setNotificationMessage("Please select a guard to notify.");
      setNotificationType("error");
      return;
    }

    const confirmNotify = window.confirm(
      "Are you sure you want to notify the guard?",
    );
    if (!confirmNotify) {
      return;
    }

    try {
      setNotificationMessage("");
      const notifySuccess = await notifyGuard(selectedUserId);
      if (notifySuccess) {
        await updateAlarmStatus("notified", selectedUserId); // Pass the guard ID
      } else {
        setAlarm((prevAlarm) => ({
          ...prevAlarm,
          status: "pending",
        }));
        setNotificationMessage(
          "Notification failed. Call the guard immediately to ensure the alert is acknowledged.",
        );
        setNotificationType("error");
      }
    } catch (err) {
      console.error("Error during notification and status update:", err);
      setNotificationMessage("Failed to update status and notify the guard.");
      setNotificationType("error");
    }
  };

  const handleDismissAlert = () => {
    const confirmDismiss = window.confirm(
      "Are you sure you want to dismiss the alarm?",
    );
    if (!confirmDismiss) {
      return;
    }
    updateAlarmStatus("ignored");
  };

  const handleManualNotifyConfirm = async () => {
    if (callChecked) {
      await updateAlarmStatus("notified");
      setNotificationMessage(
        "Manual notification confirmed. Status updated to notified.",
      );
      setNotificationType("success");
      setManualNotifyVisible(false);
    } else {
      setNotificationMessage(
        "Please call the guard and check Call to confirm manual notification.",
      );
      setNotificationType("error");
    }
  };

  return (
    <div className="bg-custom-bg min-h-screen max-h-screen flex flex-col overflow-hidden">
      <Header />
      <div className="flex-grow flex flex-col items-center p-8 overflow-hidden">
        <div className="flex w-11/12 justify-between bg-custom-bg max-w-6xl overflow-hidden">
          <div className="w-2/5 overflow-hidden">
            <img
              src={liveFootage}
              alt="Live footage"
              className="w-full h-full object-contain rounded-lg"
            />
          </div>
          <div className="w-2/5 bg-gray-200 rounded-lg p-2 ml-2 overflow-y-auto max-h-[300px]">
            {alarm ? (
              <>
                <p className="text-xl font-semibold mb-2">
                  Alert number: {alarm.id || "N/A"}
                </p>
                <p className="text-lg">Camera ID: {alarm.camera_id}</p>
                <p className="text-lg">Type: {alarm.type}</p>
                <p className="text-lg">
                  Confidence Level:{" "}
                  {alarm.confidence_score
                    ? (alarm.confidence_score * 100).toFixed(2) + "%"
                    : "N/A"}
                </p>
                <p className="text-lg">
                  Timestamp:{" "}
                  {alarm.timestamp !== "N/A"
                    ? new Date(alarm.timestamp).toLocaleString()
                    : "N/A"}
                </p>
                <p className="text-lg">Operator ID: {alarm.operator_id}</p>
                <p className="text-lg">Status: {alarm.status}</p>
              </>
            ) : (
              <p>Loading alarm details...</p>
            )}
          </div>
        </div>
        {alarm?.status !== "resolved" && (
          <div className="flex flex-col items-center w-10/12 max-w-6xl mt-6 overflow-hidden">
            {alarm?.status === "notified" ? (
              <div className="flex justify-center w-full">
                <button
                  onClick={() => updateAlarmStatus("resolved")}
                  className="bg-[#EBB305] text-white px-6 py-3 rounded-lg hover:bg-[#FACC14] transition duration-200"
                >
                  Resolve Alarm
                </button>
              </div>
            ) : (
              <div className="flex justify-between w-full">
                <button
                  onClick={() => navigate("/live-feed", { state: { id } })}
                  className="bg-[#237F94] text-white px-6 py-3 rounded-lg hover:bg-[#1E6D7C] transition duration-200"
                >
                  Look at the live feed
                </button>
                <div>
                  <select
                    value={selectedUserId}
                    onChange={(e) => setSelectedUserId(e.target.value)}
                    className="border p-2 rounded-md"
                  >
                    <option value="">Select a guard</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.username}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={handleNotifyAndUpdate}
                    className="ml-2 bg-[#237F94] text-white px-6 py-3 rounded-lg hover:bg-[#1E6D7C] transition duration-200"
                  >
                    Notify the Guard
                  </button>
                </div>
                <button
                  onClick={handleDismissAlert}
                  className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition duration-200"
                >
                  Dismiss the alert
                </button>
              </div>
            )}
            <div className="mt-2 h-20 flex flex-col items-center">
              {notificationMessage && (
                <p
                  className={`text-center ${
                    notificationType === "success"
                      ? "text-green-500"
                      : "text-red-500"
                  }`}
                >
                  {notificationMessage}
                </p>
              )}
              {manualNotifyVisible && (
                <div className="mt-2 flex space-x-2 items-center">
                  <label className="flex items-center space-x-1">
                    <input
                      type="checkbox"
                      checked={callChecked}
                      onChange={() => setCallChecked(!callChecked)}
                      className="form-checkbox"
                    />
                    <span>Confirm call and manual alert handling.</span>
                  </label>
                  <button
                    onClick={handleManualNotifyConfirm}
                    className="bg-[#237F94] text-white px-2 py-2 rounded-lg hover:bg-[#1E6D7C] transition duration-200"
                  >
                    Confirm
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlarmDetailPage;
