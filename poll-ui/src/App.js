// import logo from './logo.svg';
import './App.css';

import ItemSelector from './components/ItemSelector';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';

function App() {
  return (
    // <div className="App">
    //   <header className="App-header">
    //     <img src={logo} className="App-logo" alt="logo" />
    //     <p>
    //       Edit <code>src/App.js</code> and save to reload.
    //     </p>
    //     <a
    //       className="App-link"
    //       href="https://reactjs.org"
    //       target="_blank"
    //       rel="noopener noreferrer"
    //     >
    //       Learn React
    //     </a>
    //   </header>
    // </div>
    
    <Container fluid className="App-header">
      
      <Row  className="justify-content-center">
        <Col md={12}>
          <Card >
            <Card.Body>
              <Card.Title><h1>JBoss Cowboys Vote Manager</h1></Card.Title>

              <ItemSelector />    

            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default App;
