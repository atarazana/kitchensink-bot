// src/components/ItemSelector.js
import React, { useState, useEffect } from 'react';

import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';
import Toast from 'react-bootstrap/Toast';
import ToastContainer from 'react-bootstrap/ToastContainer';
import Badge from 'react-bootstrap/Badge';

import { v4 as uuidv4 } from 'uuid';

function ItemSelector() {
  const queryParams = new URLSearchParams(window.location.search);
  const debug = queryParams.get('debug');

  const [error, setError] = useState(undefined);
  const [success, setSuccess] = useState(undefined);

  const [poll, setPoll] = useState(undefined);
  const [selectedOption, setSelectedOption] = useState('');
  const [uniqueId, setUniqueId] = useState('');

  const radioOptions = [
    { id: "option_1", value: 'option_1', label: 'Option 1' },
    { id: "option_2", value: 'option_2', label: 'Option 2' },
    { id: "option_3", value: 'option_3', label: 'Option 3' },
  ];

  // Function to fetch data from the API
  const fetchOpenPolls = async () => {
    try {
      console.log("error: " + error)

      const response = await fetch('/poll/open');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const result = await response.json();

      if (result.length > 1) {
        console.log("There should be only one poll open at a time!");
      } else if (result.length === 1) {
        setPoll(result[0]);
        console.log("Poll open found: " + JSON.stringify(poll));
      } else {
        console.log("No polls open found!");
        setPoll(undefined);
        setSelectedOption('');
      }
    } catch (error) {
      console.error('Error fetching items:', error);
      setError('Error fetching items: ' + error);
    }
  };

  useEffect(() => {
    setError(undefined);

    // Check if a unique identifier is already stored in localStorage
    const storedUniqueId = localStorage.getItem('uniqueId');

    if (storedUniqueId) {
      // If it exists, use it
      setUniqueId(storedUniqueId);
    } else {
      // If not, generate a new unique identifier and store it
      const newUniqueId = uuidv4();
      localStorage.setItem('uniqueId', newUniqueId);
      setUniqueId(newUniqueId);
    }

    // Call the fetchOpenPolls function initially when the component mounts
    fetchOpenPolls();

    // Set up an interval to periodically call the API (e.g., every 2 seconds)
    const intervalId = setInterval(fetchOpenPolls, 2000);

    // Clean up the interval when the component unmounts
    return () => clearInterval(intervalId);
  }, []); // The empty array means this effect runs once on mount

  const handleOptionChange = (event) => {
    setSelectedOption(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    
    // Send a POST request to your second API endpoint
    if (poll !== undefined && poll.poll_name !== undefined) {
      fetch('/vote/' + poll.poll_name + '/' + uniqueId + '/' + selectedOption, {
        method: 'GET'
      })
        .then((response) => response.json())
        .then((data) => {
          console.log('Response from second API:', data);
          if (data.error) {
            setError(data.error);
          } else {
            setSelectedOption('');
            setSuccess(true)
          }
        })
        .catch((error) => {
          console.error('Error posting data:', error);
          setError('Error posting data: ' + error);
        });

    } else {
      setError("Poll was closed while trying to vote");
    }
    
  };

  const cleanError = () => {
    setError(undefined);
  };

  const cleanSuccess = () => {
    setSuccess(undefined);
  };

  return (
    <Form>
      {poll ? <Alert key="a1" variant="primary" style={{ maxWidth: '800px', wordWrap: 'break-word' }}>{poll.title}</Alert> :  <Alert key="a1" variant="danger">No poll open, checking!</Alert>}

      
      {poll && <Form.Group className="mb-3" controlId='radios' key='radios'>
      <h2>Select an option:</h2>
      {debug && <Badge bg="secondary">{uniqueId}</Badge>}
      {radioOptions.map((option) => (
        <Form.Check
        key={option.id}
        type="radio"
        id={option.id}
        label={poll[option.id]}
        value={option.id}
        checked={selectedOption === option.id}
        onChange={handleOptionChange}
        />
      ))}
      </Form.Group>}

      <Button disabled={!selectedOption} type="submit" onClick={handleSubmit}>Vote</Button>

      <ToastContainer
         position='middle-center'>
          {error !== undefined && <Toast onClose={cleanError} show={error !== undefined}>
            <Toast.Header closeButton={true}>
              <strong className="me-auto">Error found</strong>
            </Toast.Header>
            <Toast.Body>{error}</Toast.Body>
          </Toast> }

          {success !== undefined &&  <Toast onClose={cleanSuccess} show={success !== undefined} delay={3000} autohide>
            <Toast.Header closeButton={true}>
              <strong className="me-auto">Success while voting</strong>
            </Toast.Header>
            <Toast.Body>Your vote was correctly registered</Toast.Body>
          </Toast>}
        </ToastContainer>
    </Form>

    
  );
}

export default ItemSelector;