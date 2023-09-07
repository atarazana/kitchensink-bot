// src/components/ItemList.js
import React, { useState, useEffect } from 'react';

function ItemList({ onSelectItem }) {
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState('');

  useEffect(() => {
    // Fetch the list of items from your API
    fetch('/poll/open')
      .then((response) => response.json())
      .then((data) => {
        setItems(data);
      })
      .catch((error) => {
        console.error('Error fetching items:', error);
      });
  }, []);

  const handleItemChange = (event) => {
    const selectedItemValue = event.target.value;
    setSelectedItem(selectedItemValue);
    onSelectItem(selectedItemValue); // Call the callback function when the item is selected
  };

  return (
    <div>
      <label>
        Select an item:
        <select value={selectedItem} onChange={handleItemChange}>
          <option value="">-- Select an item --</option>
          {items.map((item) => (
            <option key={item.poll_name} value={item.poll_name}>
              {item.poll_name}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}

export default ItemList;