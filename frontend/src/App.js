import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Row, Col, Card, Button, Spinner, Alert } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Set the API URL based on environment
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  // Fetch data on component mount
  useEffect(() => {
    fetchData();
  }, []);

  // Function to fetch data from API
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_URL}/api/count`);
      setData(response.data);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Function to manually refresh data
  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      setError(null);
      const response = await axios.post(`${API_URL}/api/refresh`);
      
      if (response.data.success) {
        setData(response.data.data);
      } else {
        setError('Failed to refresh data. Please try again.');
      }
    } catch (err) {
      console.error('Error refreshing data:', err);
      setError('Failed to refresh data. Please try again later.');
    } finally {
      setRefreshing(false);
    }
  };

  // Format date string
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  return (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          <Card className="shadow-sm">
            <Card.Header className="bg-primary text-white">
              <h4 className="mb-0">SIH Submission Monitor</h4>
            </Card.Header>
            <Card.Body>
              {error && <Alert variant="danger">{error}</Alert>}
              
              {loading ? (
                <div className="text-center py-5">
                  <Spinner animation="border" variant="primary" />
                  <p className="mt-3">Loading data...</p>
                </div>
              ) : (
                <>
                  {data?.error && (
                    <Alert variant="warning" className="mb-3">
                      <Alert.Heading>Monitoring Issue</Alert.Heading>
                      <p className="mb-0">{data.error}</p>
                      {data.status === 'blocked' && (
                        <hr />
                        <p className="mb-0 small">
                          The SIH website may be blocking automated requests. 
                          This is temporary and the system will keep trying.
                        </p>
                      )}
                    </Alert>
                  )}
                  
                  <div className="mb-4">
                    <h2 className="text-center display-4 mb-0">
                      {data?.count !== null && data?.count !== undefined ? data?.count : 'N/A'}
                    </h2>
                    <p className="text-center text-muted">
                      Current Submissions
                      {data?.status === 'blocked' && (
                        <span className="badge bg-warning text-dark ms-2">Blocked</span>
                      )}
                    </p>
                  </div>
                  
                  <div className="mb-3">
                    <p className="mb-1"><strong>Problem ID:</strong> {data?.problem_id || 'N/A'}</p>
                    <p className="mb-1"><strong>Last Updated:</strong> {formatDate(data?.last_refresh)}</p>
                    <p className="mb-0 text-muted small">
                      Auto-refreshes every hour
                      {data?.status === 'blocked' && ' (currently blocked)'}
                    </p>
                  </div>
                </>
              )}
              
              <div className="d-grid gap-2 mt-3">
                <Button 
                  variant="primary" 
                  onClick={handleRefresh} 
                  disabled={refreshing || loading}
                >
                  {refreshing ? (
                    <>
                      <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />
                      <span className="ms-2">Refreshing...</span>
                    </>
                  ) : 'Refresh Now'}
                </Button>
              </div>
            </Card.Body>
            <Card.Footer className="text-center text-muted">
              <small>Data refreshes automatically every hour</small>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default App;