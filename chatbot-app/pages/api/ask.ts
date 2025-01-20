// pages/api/ask.ts
import type { NextApiRequest, NextApiResponse } from 'next';


export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'POST') {
    const { question } = req.body;

    if (!question) {
      return res.status(400).json({ error: 'No question provided' });
    }

    try {
      if (!process.env.KOYEB_API) {
        throw new Error('KOYEB_API environment variable is not defined');
      }
      
      // Call the Flask backend
      const response = await fetch(process.env.KOYEB_API , {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept':'application/json'
        },
        body: JSON.stringify({ question }),
      });

      // Check if the response is OK
      if (!response.ok) {
        throw new Error(`Flask backend returned ${response.status}: ${response.statusText}`);
      }

      // Parse the response as JSON
      const text = await response.text(); // First, get the raw text
      let data;
      try {
        data = JSON.parse(text); // Try to parse it as JSON
      } catch (e) {
        throw new Error(`Invalid JSON response from Flask backend: ${text}`);
      }

      res.status(200).json(data);
    } catch (error) {
      console.error('Error calling Flask backend:', error);
      res.status(500).json({ error: 'Failed to fetch answer' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}