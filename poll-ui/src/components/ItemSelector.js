// src/components/ItemSelector.js
import React, { useState, useEffect } from 'react';

import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';
import Toast from 'react-bootstrap/Toast';
import ToastContainer from 'react-bootstrap/ToastContainer';

import { v4 as uuidv4 } from 'uuid';

function ItemSelector() {
  const [error, setError] = useState(undefined);

  const [poll, setPoll] = useState(undefined);
  const [previousPoll, setPreviousPoll] = useState(undefined);
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
      } else if (result.length == 1) {
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
            setPreviousPoll(poll);
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

  return (
    
    <Form>
      {poll ? <Alert key="a1" variant="primary" style={{ maxWidth: '800px', wordWrap: 'break-word' }}>{poll.title}</Alert> :  <Alert key="a1" variant="danger">No poll open, checking!</Alert>}

      
      {poll && <Form.Group className="mb-3" controlId='radios' key='radios'>
      <h2>Select an Option:</h2>
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

      {/* {fetchError != undefined && fetchError !== "" && <Alert key="a2" variant="danger">{fetchError}</Alert>}

      {voteError != undefined && voteError !== "" && <Alert key="a3" variant="danger">{voteError}</Alert>} */}
      
      {error != undefined && <div
        aria-live="polite"
        aria-atomic="true"
        className="position-relative"
        style={{ minHeight: '240px' }}
      >
        <ToastContainer
          className="p-3"
          position="middle-center"
          style={{ zIndex: 1 }}
        >
          <Toast onClose={cleanError}>
            <Toast.Header closeButton={true}>
              <strong className="me-auto">Error while trying to vote</strong>
              <small>Seconds ago</small>
            </Toast.Header>
            <Toast.Body>{error}</Toast.Body>
          </Toast>
        </ToastContainer>
      </div>}

    </Form>
    
  );
}

export default ItemSelector;