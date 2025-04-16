import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const UserAuth = ({ isRegister = false }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = isRegister 
        ? 'http://localhost:8000/register' 
        : 'http://localhost:8000/login';
      
      const response = await axios.post(url, formData);
      
      if (isRegister) {
        toast.success('Registration successful!');
        navigate('/login');
      } else {
        toast.success('Login successful!');
        localStorage.setItem('userId', response.data.user_id);
        navigate('/');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div className="auth-form">
      <h2>{isRegister ? 'Register' : 'Login'}</h2>
      <form onSubmit={handleSubmit}>
        {isRegister && (
          <input
            type="text"
            placeholder="Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
        )}
        <input
          type="email"
          placeholder="Email"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={formData.password}
          onChange={(e) => setFormData({...formData, password: e.target.value})}
          required
        />
        <button type="submit">{isRegister ? 'Register' : 'Login'}</button>
      </form>
    </div>
  );
};

export default UserAuth;