# Ticket-Booking-Manager
# 🎫 Alibaba Travel Ticket Reservation System

A comprehensive full-stack travel ticket reservation platform that enables users to book, manage, and track transportation tickets across multiple modes (bus, train, and plane) with advanced analytical capabilities and enterprise-grade performance optimizations.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Database Design](#database-design)
- [API Reference](#api-reference)
- [Installation & Setup](#installation--setup)
- [Performance Optimizations](#performance-optimizations)
- [Testing](#testing)
- [Future Enhancements](#future-enhancements)
- [Team](#team)

## 🚀 Project Overview

The Alibaba Travel Ticket Reservation System is a sophisticated backend platform designed to handle complex travel booking operations with high performance and reliability. The system evolved through multiple phases:

- **Phase 1**: Core database design and basic CRUD operations
- **Phase 2**: Advanced analytics, stored procedures, and query optimization
- **Phase 3**: RESTful API development with authentication and caching

The system supports multi-modal transportation (bus, train, plane) with comprehensive user management, reservation tracking, payment processing, and administrative oversight.

## 🏗 System Architecture

### Backend Framework
- **Framework**: Flask (Python) for RESTful API development
- **Database**: MySQL for persistent data storage
- **Caching**: Redis for frequently accessed data and search results
- **Authentication**: JWT tokens for stateless, secure authentication
- **Modular Design**: Flask Blueprints for organized API endpoints

### Architectural Layers
1. **API Layer**: HTTP request handling, input validation, JWT verification
2. **Service Layer**: Business logic orchestration
3. **Database Layer**: Raw SQL queries with parameterization for security
4. **Caching Layer**: Redis integration for performance optimization

## ✨ Key Features

### 🔐 Authentication & User Management
- OTP-based login system with email verification
- JWT token-based authentication
- User registration and profile management
- Secure password hashing

### 🎫 Ticket Management
- Multi-modal ticket search (bus, train, plane)
- Advanced filtering (price range, date, company, class)
- Real-time seat availability
- Dynamic pricing

### 📅 Reservation System
- Time-limited reservations with automatic expiration
- Active reservation tracking
- Reservation history
- Bulk reservation support

### 💳 Payment Integration
- Multiple payment methods support
- Transaction status tracking
- Refund processing
- Payment verification

### 🛠 Administrative Features
- Support ticket management
- Cancellation tracking and analytics
- User reporting system
- Dashboard for business insights

### 📊 Advanced Analytics
- Monthly payment aggregation per user
- Top customer identification
- Transportation mode analytics
- Geographic sales analysis
- Cancellation pattern tracking

## 🛠 Technology Stack

### Backend
- **Python 3.8+** with Flask framework
- **MySQL** with advanced indexing strategies
- **Redis** for caching and session management
- **JWT** for authentication

### Database Optimization
- **Indexing Strategy**: Multi-column indexes, covering indexes
- **Stored Procedures**: 8+ optimized procedures for common operations
- **Query Optimization**: Early filtering, selective column fetching, temporal filtering
- **ENUM Types**: For status and transportation mode restrictions

## 🗄 Database Design

### Normalization
- **3NF Compliance**: All attributes fully dependent on primary keys
- **Transitive Dependencies**: Removed through proper table segregation
- **Referential Integrity**: ON DELETE and ON UPDATE constraints

### Key Entities
- **Person**: Base user information with polymorphic relationships
- **Passenger**: Extended user profile with loyalty tracking
- **Support**: Administrative staff accounts
- **Vehicle**: Base transportation entity with subtype tables (Bus, Train, Plane)
- **Ticket**: Booking records with spatial and temporal data
- **Reservation**: User booking sessions
- **Payment**: Financial transaction records
- **Report**: User issue tracking and support responses

### Indexing Strategy
| Table | Primary Key | Indexed Columns | Purpose |
|-------|-------------|-----------------|---------|
| person | person_id | email, phone_number, city | Identity & geographic search |
| ticket | ticket_id | vehicle_id, reservation_id, created_at | Vehicle/date/reservation filtering |
| reservation | reservation_id | passenger_id, status | Cancellation & passenger history |
| vehicle | vehicle_id | vehicle_type | Transport type access |
| report | report_id | ticket_id, report_subject | Complaint type grouping |

## 🌐 API Reference

### Authentication Endpoints
- `POST /api/auth/login/request-otp` - Request OTP for login
- `POST /api/auth/login/verify-otp` - Verify OTP and receive JWT
- `POST /api/auth/signup` - User registration
- `POST /api/auth/profile/update` - Update user profile

### Ticket Endpoints
- `GET /api/tickets/search` - Search tickets with filters
- `GET /api/tickets/details/<ticket_id>` - Get ticket details

### Reservation Endpoints
- `POST /api/reservations/reserve` - Create new reservation
- `GET /api/reservations/active` - Get active reservations
- `GET /api/reservations/history` - Get reservation history

### City Endpoints
- `GET /api/cities` - Get available cities

### Administrative Endpoints
- `GET /api/admin/reservations` - Admin reservation management
- `GET /api/admin/payments` - Payment status monitoring
- `GET /api/admin/reports` - User report management

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- Redis Server

### Installation Steps
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alibaba-travel-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Configuration**
   - Update `config.py` with MySQL connection details
   - Configure Redis connection settings
   - Set JWT secret keys and expiration

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the API**
   - Base URL: `http://localhost:5000`

### Configuration
Key configuration files:
- `config.py` - Database, Redis, and JWT settings
- Database schema initialization scripts
- Sample data population scripts (using Faker library)

## 🚀 Performance Optimizations

### Query Optimization Techniques
- **Strategic Indexing**: On search-heavy fields (dates, city, transport mode)
- **ENUM Columns**: For status and type fields to avoid string matching
- **Early Filtering**: Push conditions like `status='CANCELLED'` before joins
- **Selective Column Fetching**: Avoid `SELECT *`, fetch only required columns
- **Temporal Filtering**: Date-range optimization for reporting

### Stored Procedures
8+ optimized stored procedures including:
- `sp_user_tickets_ordered` - User ticket history
- `sp_city_tickets` - Geographic ticket analysis
- `sp_top_n_buyers` - Frequent buyer identification
- `sp_phrase_search` - Text-based ticket search

### Caching Strategy
- Redis caching for frequent search queries
- Cache key generation from query parameters
- JSON serialization with datetime handling
- Automatic cache invalidation on data updates

## 🧪 Testing

### API Testing with Postman
Comprehensive test suite covering:
1. **Authentication Flow**: OTP request/verification, signup
2. **Ticket Operations**: Search, details, filtering
3. **Reservation Management**: Create, view active, history
4. **Payment Processing**: Transaction flow, status updates
5. **Administrative Functions**: User management, reporting

### Test Coverage
- Unit tests for service layer functions
- Integration tests for API endpoints
- Database transaction tests
- Error handling and edge cases

## 🔮 Future Enhancements

### Planned Features
- **Materialized Views** for heavy aggregated queries
- **Table Partitioning** on ticket table (by date/month)
- **Advanced Caching** layer for stored procedures
- **Automated Triggers** for loyalty point updates
- **Passenger Scoring Function** based on loyalty, spend, and travel patterns

### Scalability Improvements
- Microservices architecture decomposition
- Load balancing and horizontal scaling
- Database read replicas for analytical queries
- Message queue for asynchronous processing

## 👥 Team

**Project Developers:**
- **Alireza Nobakht**
- **Mohammad Taghi Ghaffari** 
- **Mahan Nojavan**

### Academic Context
This project was developed as part of database system coursework, demonstrating enterprise-level best practices in database design, API development, and system optimization.

---

## 📄 License

This project is developed for academic purposes as part of database management system coursework.

---

*For detailed technical documentation, database schema diagrams, and implementation specifics, refer to the phase-specific documentation files included in the repository.*
