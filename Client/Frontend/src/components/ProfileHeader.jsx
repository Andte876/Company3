import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";
import bellIcon from "../assets/bell-01.png";

const Header = ({ userInfo, setErrorMessage }) => {
  const navigate = useNavigate();

  // Function to navigate based on the user's role
  const navigateToHome = () => {
    switch (userInfo.role.toLowerCase()) {
      case "admin":
        navigate("/admin");
        break;
      case "operator":
        navigate("/operator");
        break;
      case "manager":
        navigate("/dashboard");
        break;
      default:
        setErrorMessage("Unknown role");
    }
  };

  return (
    <header className="relative flex items-center p-4 bg-[#F5F7FA] border-b">
      {/* Centered Logo */}
      <img
        src={logo}
        alt="PanoraGuard logo"
        className="absolute left-1/2 transform -translate-x-1/2 h-5"
      />

      {/* Right Notification Icon */}
      <div className="ml-auto">
        <button onClick={navigateToHome}>
          <img
            src={bellIcon}
            alt="Notification icon"
            className="w-6 h-6 hover:scale-110 transition-transform duration-200"
          />
        </button>
      </div>
    </header>
  );
};

export default Header;
