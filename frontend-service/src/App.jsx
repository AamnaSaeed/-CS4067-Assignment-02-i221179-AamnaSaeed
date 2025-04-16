import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import EventList from './components/EventList'
import UserAuth from './components/UserAuth'
import BookingForm from './components/BookingForm'

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <div className="content">
        <Routes>
          <Route path="/" element={<EventList />} />
          <Route path="/login" element={<UserAuth />} />
          <Route path="/register" element={<UserAuth isRegister />} />
          <Route path="/book/:eventId" element={<BookingForm />} />
        </Routes>
      </div>
    </div>
  )
}