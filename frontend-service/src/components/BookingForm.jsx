import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const BookingForm = () => {
  const { eventId } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [tickets, setTickets] = useState(1);
  const userId = localStorage.getItem('userId');

  useEffect(() => {
    if (!userId) {
      toast.error('Please login to book tickets');
      navigate('/login');
      return;
    }

    const fetchEvent = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/events`);
        const foundEvent = response.data.find(e => e.id === parseInt(eventId));
        if (foundEvent) {
          setEvent(foundEvent);
        } else {
          toast.error('Event not found');
          navigate('/');
        }
      } catch (error) {
        toast.error('Failed to fetch event details');
      }
    };
    fetchEvent();
  }, [eventId, navigate, userId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/bookings', {
        user_id: userId,
        event_id: eventId,
        tickets: tickets
      });
      toast.success('Booking successful!');
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Booking failed');
    }
  };

  if (!event) return <div>Loading...</div>;

  return (
    <div className="booking-form">
      <h2>Book Tickets for {event.name}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Number of Tickets:</label>
          <input
            type="number"
            min="1"
            value={tickets}
            onChange={(e) => setTickets(parseInt(e.target.value))}
            required
          />
        </div>
        <button type="submit">Confirm Booking</button>
      </form>
    </div>
  );
};

export default BookingForm;