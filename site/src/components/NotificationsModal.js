import React, { useEffect, useState } from 'react';
import './NotificationsModal.css';
import apiService from '../services/api';

const NotificationsModal = ({ email, onClose }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiService.getNotifications(email);
        setNotifications(data);
      } catch (e) {
        setError('Failed to load messages');
      } finally {
        setLoading(false);
      }
    };
    if (email) load();
  }, [email]);

  const markRead = async (id) => {
    try {
      await apiService.markNotificationRead(id);
      setNotifications((prev) => prev.map(n => n.id === id ? { ...n, is_read: 1 } : n));
    } catch (_) {}
  };

  const markAllRead = async () => {
    const unreadIds = notifications.filter(n => !n.is_read).map(n => n.id);
    for (const id of unreadIds) {
      try { await apiService.markNotificationRead(id); } catch (_) {}
    }
    setNotifications((prev) => prev.map(n => ({ ...n, is_read: 1 })));
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="notif-backdrop" onClick={onClose}>
      <div className="notif-modal" onClick={(e) => e.stopPropagation()}>
        <div className="notif-header">
          <div className="notif-title-wrap">
            <h3>Messages</h3>
            {unreadCount > 0 && <span className="notif-badge">{unreadCount}</span>}
          </div>
          <div className="notif-actions">
            {unreadCount > 0 && (
              <button className="mark-all" onClick={markAllRead}>Mark all read</button>
            )}
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
        </div>
        <div className="notif-body">
          {loading ? (
            <div className="notif-loading">Loading…</div>
          ) : error ? (
            <div className="notif-error">{error}</div>
          ) : notifications.length === 0 ? (
            <div className="notif-empty">No messages yet</div>
          ) : (
            <ul className="notif-list">
              {notifications.map((n) => (
                <li key={n.id} className={`notif-item ${n.is_read ? 'read' : 'unread'} ${n.type || 'info'}`}>
                  <div className="notif-item-head">
                    <div className="notif-dot" />
                    <div className="notif-item-title">{n.title}</div>
                    <div className="notif-time">{new Date(n.created_at).toLocaleString()}</div>
                  </div>
                  <div className="notif-message">{n.message}</div>
                  {!n.is_read && (
                    <div className="notif-item-actions">
                      <button className="mark-read" onClick={() => markRead(n.id)}>Mark read</button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default NotificationsModal;
