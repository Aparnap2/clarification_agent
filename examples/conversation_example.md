# Conversation Example: Building a Task Management App

This example shows how the Clarification Agent guides a user through planning a task management application.

## Starting the Conversation

**Agent**: I'm your AI Clarification Agent. I'll help you define and scope your project by asking questions from different perspectives. Let's start with the basics:

What is the project you want to build? Please describe it briefly.

**User**: I want to build a task management app that helps teams collaborate on projects. It should have features like task assignment, due dates, comments, and progress tracking.

## Product Manager Perspective

**Agent (Product Manager)**: As a Product Manager, I'm focused on user needs and product features. Based on what you've shared, what are the 3-5 most important features that would deliver the most value to your users in the MVP?

**User**: I think the most important features are:
1. Task creation and assignment
2. Due date setting and reminders
3. Comments on tasks
4. Simple progress tracking (not started, in progress, completed)
5. Team member management

## Scope Reduction

**Agent**: Now let's focus on scope reduction. For an MVP (Minimum Viable Product), it's important to identify what features are essential and what can be left for later versions.

What features or capabilities do you think should NOT be included in the initial MVP?

**User**: For the MVP, we can exclude:
- Advanced reporting and analytics
- Time tracking
- Custom fields
- Integrations with other tools
- Mobile app (we'll start with web only)

## Business Analyst Perspective

**Agent (Business Analyst)**: Looking at this from a business perspective, who are your target users or customers? And what specific problem does this project solve for them that they can't solve with existing solutions?

**User**: Our target users are small to medium-sized teams (5-20 people) who find existing tools either too complex or too simple. We're solving the problem of task visibility and accountability without the overhead of learning complex project management software.

## Technology Selection

**Agent**: Let's talk about technology choices. Based on your project description, here are some suggestions:

Frontend: React with Material UI
Backend: Node.js with Express
Database: PostgreSQL for structured data
Authentication: Auth0 for secure user management
Deployment: Docker containers on AWS for scalability

What technologies would you like to use for this project? Feel free to choose from these suggestions or specify your own preferences.

**User**: Those suggestions look good, but I'd like to use:
- Frontend: React with Chakra UI
- Backend: Node.js with Express
- Database: MongoDB (we prefer document DB for flexibility)
- Authentication: Firebase Auth
- Deployment: Vercel for frontend, Heroku for backend

## Tech Lead Perspective

**Agent (Tech Lead)**: From a technical perspective, I'd like to understand more about your constraints. Are there any specific technical requirements, performance needs, or scalability concerns we should consider in the architecture?

**User**: We expect to have around 100 users initially, but it should be able to scale to 1000+ users. Each team might have hundreds of tasks, so we need good performance when filtering and searching tasks. We also need to consider real-time updates when team members modify tasks.

## File Structure

**Agent**: Based on your technology choices, here's a suggested file structure for your project:

- client/
  - src/
    - components/
      - TaskList.js: Component to display list of tasks
      - TaskItem.js: Individual task component
      - TaskForm.js: Form for creating/editing tasks
      - TeamManagement.js: Team member management component
    - pages/
      - Dashboard.js: Main dashboard page
      - Auth.js: Authentication pages
    - context/
      - AuthContext.js: Authentication context
      - TaskContext.js: Task data context
    - utils/
      - api.js: API communication functions
- server/
  - models/
    - Task.js: Task data model
    - User.js: User data model
    - Team.js: Team data model
  - routes/
    - tasks.js: Task API endpoints
    - users.js: User API endpoints
    - teams.js: Team API endpoints
  - middleware/
    - auth.js: Authentication middleware
  - app.js: Express application
  - server.js: Server entry point

Does this structure look good to you? Would you like to make any changes or additions?

**User**: That looks good! Maybe we should add a notifications.js model and route for task reminders and notifications.

## UX Designer Perspective

**Agent (UX Designer)**: From a user experience standpoint, what are the key user journeys or workflows that need to be smooth and intuitive in your application?

**User**: The most important workflows are:
1. Creating and assigning a task
2. Viewing tasks assigned to me
3. Updating task status
4. Adding comments to tasks
5. Setting up a new team and inviting members

## Task Planning

**Agent**: Let's break down the project into actionable tasks. Here are the key tasks I recommend:

- Set up React project with Chakra UI (4h, priority: 1)
- Create Express server with MongoDB connection (3h, priority: 1)
- Implement user authentication with Firebase (5h, priority: 1)
- Create task data model and API endpoints (4h, priority: 2)
- Build task list and task detail components (6h, priority: 2)

Do these tasks cover the essential work needed for your MVP? Would you like to add or modify any tasks?

**User**: Those look good, but we should also add:
- Team management UI and API (5h, priority: 2)
- Task filtering and search functionality (4h, priority: 3)
- Email notifications for task assignments and due dates (6h, priority: 3)

## QA Engineer Perspective

**Agent (QA Engineer)**: Thinking about quality and testing, what are the critical aspects of the application that absolutely must work correctly? And are there any edge cases we should plan for?

**User**: The task assignment and due date functionality must work flawlessly. We should plan for edge cases like:
- Users in different time zones seeing correct due dates
- Handling task reassignment when a team member is removed
- Ensuring proper access controls (users should only see tasks for their teams)
- Handling offline/poor connection scenarios gracefully

## Summary

**Agent**: Great! I've completed the project clarification process. Here's a summary:

# Project Summary: Task Management App

## Description
A collaborative task management application for small to medium-sized teams with features for task assignment, due dates, comments, and progress tracking.

## MVP Features
- Task creation and assignment
- Due date setting and reminders
- Comments on tasks
- Simple progress tracking
- Team member management

## Excluded from MVP
- Advanced reporting and analytics
- Time tracking
- Custom fields
- Integrations with other tools
- Mobile app

## Technology Stack
- Frontend: React with Chakra UI
- Backend: Node.js with Express
- Database: MongoDB
- Authentication: Firebase Auth
- Deployment: Vercel for frontend, Heroku for backend

## Next Steps
1. Review the generated files in the project directory
2. Start implementing the MVP based on the task plan
3. Iterate and refine as you build

I've generated the necessary files for your project. You can find them in the project directory.