import React, { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import Icon from './Icon';
import './StripePayment.css';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

const CheckoutForm = ({ amount, onSuccess, onCancel, parkingSpace, selectedHours }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState(null);
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setProcessing(true);
    setError(null);

    const card = elements.getElement(CardElement);

    // In a real app, you would call your backend to create a payment intent
    // For now, we'll simulate a successful payment
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simulate payment success
      const paymentResult = {
        id: `pi_${Math.random().toString(36).substr(2, 9)}`,
        amount: amount * 100, // Stripe amounts are in cents
        status: 'succeeded'
      };

      setProcessing(false);
      onSuccess(paymentResult);
    } catch (err) {
      setError('Payment failed. Please try again.');
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="checkout-form">
      <div className="payment-summary">
        <h3>Payment Summary</h3>
        <div className="summary-row">
          <span>Parking Space #{parkingSpace.id.split('-')[1]}</span>
          <span>${parkingSpace.price}/{parkingSpace.paymentType === 'hourly' ? 'hr' : 'flat'}</span>
        </div>
        {parkingSpace.paymentType === 'hourly' && (
          <div className="summary-row">
            <span>{selectedHours} hours</span>
            <span>${(parkingSpace.price * selectedHours).toFixed(2)}</span>
          </div>
        )}
        <div className="summary-row total">
          <span>Total</span>
          <span>${amount.toFixed(2)}</span>
        </div>
      </div>

      <div className="card-element-container">
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': {
                  color: '#aab7c4',
                },
              },
            },
          }}
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="payment-buttons">
        <button
          type="button"
          onClick={onCancel}
          className="cancel-button"
          disabled={processing}
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={!stripe || processing}
          className="pay-button"
        >
          {processing ? (
            <>
              <div className="spinner"></div>
              Processing...
            </>
          ) : (
            <>
              <Icon name="credit-card" size={16} />
              Pay ${amount.toFixed(2)}
            </>
          )}
        </button>
      </div>
    </form>
  );
};

const StripePayment = ({ amount, onSuccess, onCancel, parkingSpace, selectedHours }) => {
  return (
    <Elements stripe={stripePromise}>
      <CheckoutForm
        amount={amount}
        onSuccess={onSuccess}
        onCancel={onCancel}
        parkingSpace={parkingSpace}
        selectedHours={selectedHours}
      />
    </Elements>
  );
};

export default StripePayment;