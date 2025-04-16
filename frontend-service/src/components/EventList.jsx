import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const EventList = () => {
  const [events, setEvents] = useState([]);
  const userId = localStorage.getItem('userId');

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await axios.get('http://localhost:8000/events');
        setEvents(response.data);
      } catch (error) {
        toast.error('Failed to fetch events');
      }
    };
    fetchEvents();
  }, []);

  return (
    <div className="event-list">
      <h2>Upcoming Events</h2>
      {events.length === 0 && <p>No events available</p>}
      <div className="events">
        {events.map(event => (
          <div key={event.id} className="event-card">
            <h3>{event.name}</h3>
            <p>Date: {event.date}</p>
            <p>Location: {event.location}</p>
            {userId && (
              <Link to={`/book/${event.id}`} className="book-btn">Book Now</Link>
            )}
            {!userId && (
              <p className="login-prompt">Please login to book</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default EventList;