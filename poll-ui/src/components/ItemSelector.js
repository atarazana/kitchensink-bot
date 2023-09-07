// src/components/ItemSelector.js
import React, { useState } from 'react';

import ItemList from './ItemList';

import { useLocation } from 'react-router-dom';


function ItemSelector() {
  // const location = useLocation()
  console.log(">> " + window.location);
  const queryParams = new URLSearchParams(window.location.search);
  const pollName = queryParams.get('poll_name');
  console.log("pollName " + pollName);

  const [selectedItem, setSelectedItem] = useState('');
  const [selectedOption, setSelectedOption] = useState('');

  const handleItemSelect = (item) => {
    console.log('item: ' + item)
    setSelectedItem(item);
  };

  const handleOptionChange = (event) => {
    setSelectedOption(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    
    // Send a POST request to your second API endpoint
    console.log("pollName: " + pollName + " selectedItem: " + selectedItem);
    const selectedPollName = pollName || selectedItem;
    fetch('/vote/' + selectedPollName + '/' + selectedOption, {
      method: 'GET',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify(postData),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Response from second API:', data);
      })
      .catch((error) => {
        console.error('Error posting data:', error);
      });
  };

  return (
    <div>
      <h2>Item Selector</h2>
      {pollName || <ItemList onSelectItem={handleItemSelect} />}
      <div>
        <h3>Select an Option:</h3>
        <label>
          Option 1
          <input
            type="radio"
            value="option_1"
            checked={selectedOption === 'option_1'}
            onChange={handleOptionChange}
          />
        </label>
        <label>
          Option 2
          <input
            type="radio"
            value="option_2"
            checked={selectedOption === 'option_2'}
            onChange={handleOptionChange}
          />
        </label>
        <label>
          Option 3
          <input
            type="radio"
            value="option_3"
            checked={selectedOption === 'option_3'}
            onChange={handleOptionChange}
          />
        </label>
      </div>
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}

export default ItemSelector;