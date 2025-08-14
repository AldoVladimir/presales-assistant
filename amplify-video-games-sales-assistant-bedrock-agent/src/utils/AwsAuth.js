const ACCESS_KEY_ID = process.env.REACT_APP_ACCESS_KEY_ID;
const SECRET_ACCESS_KEY = process.env.REACT_APP_SECRET_ACCESS_KEY;
const REGION = process.env.REACT_APP_REGION;

/**
 * Creates client for a specific AWS service with authenticated credentials
 * @param {Function} ClientConstructor - AWS SDK client constructor
 * @param {Object} options - Additional client options
 * @returns {Promise<Object>} Configured AWS service client
 */
export const createAwsClient = (ClientConstructor, options = {}) => {
  // Create client configuration
  const clientConfig = {
    region: REGION,
    credentials: {
      accessKeyId: ACCESS_KEY_ID,
      secretAccessKey: SECRET_ACCESS_KEY
    },
    ...options,
  };

  return new ClientConstructor(clientConfig);
};