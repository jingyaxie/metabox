import React from 'react';
import Layout from '../components/Layout';
import EnhancedRetrievalPanel from '../components/EnhancedRetrievalPanel';

const EnhancedRetrieval: React.FC = () => {
  return (
    <Layout>
      <div className="p-6">
        <EnhancedRetrievalPanel />
      </div>
    </Layout>
  );
};

export default EnhancedRetrieval; 