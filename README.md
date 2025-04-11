# Diabetes Risk Predictor

A comprehensive web application for diabetes risk assessment, health tracking, and education built with Django and modern UI components.

![App Screenshot](https://via.placeholder.com/800x400?text=Diabetes+Predictor+App)

## Features

- **Risk Prediction:** Advanced machine learning model to predict diabetes risk based on health metrics
- **Health Tracking:** Tools to track weight, blood sugar, activity levels, and sleep patterns
- **Personalized Dashboard:** Visualize your health data with interactive charts and insights
- **Educational Resources:** Learn about diabetes types, symptoms, management, and myths
- **User Management:** Secure authentication and personalized health profiles
- **Data Export:** Export your health data in JSON format for external use
- **Mobile Responsive:** Optimized for all device sizes with a modern, intuitive interface

## Technology Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, Tailwind CSS, JavaScript
- **Machine Learning:** scikit-learn
- **Data Visualization:** Chart.js
- **Icons:** Font Awesome

## Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/diabetes-predictor.git
   cd diabetes-predictor
   ```

2. Set up a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Apply database migrations
   ```
   python manage.py migrate
   ```

5. Create a superuser (optional)
   ```
   python manage.py createsuperuser
   ```

6. Run the development server
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Application Structure

- **Prediction Module:** Enter health metrics to get diabetes risk assessment
- **Tracker Module:** Log and monitor your health metrics over time
- **Dashboard:** Visualize your health data with charts and trends
- **Profile Management:** Update personal information and view health summary
- **Education Center:** Access information about diabetes types, symptoms, and management
- **Resources:** Links to external resources and helpful information

## Data Privacy

- All health data is stored securely in a database
- User authentication required for accessing and storing personal data
- No data is shared with third parties
- All sensitive information is properly protected

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

## Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/diabetes-predictor](https://github.com/yourusername/diabetes-predictor) 