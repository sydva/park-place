import React from 'react';
import Icon from './Icon';
import './ConfirmModal.css';

const ConfirmModal = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmButtonStyle = 'danger' // 'danger', 'primary', 'success'
}) => {
  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  const getConfirmButtonClass = () => {
    switch (confirmButtonStyle) {
      case 'danger':
        return 'confirm-button danger';
      case 'success':
        return 'confirm-button success';
      case 'primary':
      default:
        return 'confirm-button primary';
    }
  };

  return (
    <div className="confirm-modal-backdrop" onClick={onClose}>
      <div className="confirm-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="confirm-modal-header">
          <h3>{title}</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="confirm-modal-body">
          <p>{message}</p>
        </div>
        
        <div className="confirm-modal-footer">
          <button className="cancel-button" onClick={onClose}>
            {cancelText}
          </button>
          <button className={getConfirmButtonClass()} onClick={handleConfirm}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;