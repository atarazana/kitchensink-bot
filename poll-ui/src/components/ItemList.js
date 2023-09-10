// src/components/ItemList.js
import React, { useState } from 'react';
import Form from 'react-bootstrap/Form';
import FloatingLabel from 'react-bootstrap/FloatingLabel';

function ItemList({ items, onSelectItem }) {
  const [selectedItem, setSelectedItem] = useState('');

  const handleItemChange = (event) => {
    const selectedItemValue = event.target.value;
    setSelectedItem(selectedItemValue);
    onSelectItem(selectedItemValue); // Call the callback function when the item is selected
  };

  return (
    <FloatingLabel
      controlId="floatingSelectGrid"
      label="Select one poll to vote"
    >
    <Form.Select aria-label="Default select example" value={selectedItem} onChange={handleItemChange} key="options" name="options">
      <option key="null" value="null">Open this select menu</option>
      {items.map((item) => (
      <option key={item.poll_name} value={item.poll_name}>
        {item.poll_name}
      </option>
      ))}
    </Form.Select>
    </FloatingLabel>
    // <div>
    //   <label>
    //     Select an item:
    //     <select value={selectedItem} onChange={handleItemChange}>
    //       <option value="">-- Select an item --</option>
    //       {items.map((item) => (
    //         <option key={item.poll_name} value={item.poll_name}>
    //           {item.poll_name}
    //         </option>
    //       ))}
    //     </select>
    //   </label>
    // </div>
  );
}

export default ItemList;