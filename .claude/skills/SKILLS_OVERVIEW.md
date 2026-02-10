# Career STU - Integrated Anthropic Skills

This document describes the Anthropic skills integrated into Career STU to enhance the learning experience with better UI, interactive content, automated testing, and visual design.

## 📦 Integrated Skills

### 1. Frontend Design (`frontend-design`)

**Purpose:** Create distinctive, production-grade frontend interfaces for Career STU's learning experience.

**Use Cases in Career STU:**
- **Course Creation UI** - Beautiful interfaces for instructors/admins to create learning pathways
- **Learning Experience Dashboard** - Engaging student-facing interfaces showing progress, pathways, and goals
- **RIASEC Assessment Interface** - Interactive, visually appealing assessment flow
- **Profile Management** - Modern UI for learner profiles and skill tracking

**How to Use:**
```bash
# In Claude Code, trigger the skill:
/frontend-design

# Example prompts:
"Create a dashboard for learners to track their learning pathway progress"
"Design a course creation interface for Career STU pathway building"
"Build a RIASEC assessment UI with 48 questions"
```

**Outputs:**
- Production-ready React components
- Modern UI with Tailwind CSS
- Responsive, accessible designs
- Avoids generic AI aesthetics

---

### 2. Web Artifacts Builder (`web-artifacts-builder`)

**Purpose:** Create elaborate, multi-component interactive web artifacts for course content.

**Use Cases in Career STU:**
- **Interactive Learning Modules** - Simulations and exercises for skill development
- **Skill Practice Widgets** - Interactive coding environments, quizzes, drag-and-drop exercises
- **Career Exploration Tools** - Interactive job market visualizations and RIASEC explorers
- **Progress Visualizations** - Interactive charts showing learning progress and skill growth

**How to Use:**
```bash
# Trigger the skill:
/web-artifacts-builder

# Example prompts:
"Create an interactive Python coding exercise for data analysis"
"Build a RIASEC type explorer with interactive personality quiz"
"Design an interactive job market dashboard showing salary trends"
```

**Outputs:**
- Complex React applications
- State management and routing
- shadcn/ui components
- Interactive simulations and widgets

---

### 3. Webapp Testing (`webapp-testing`)

**Purpose:** Automated E2E testing and interaction with Career STU's web applications using Playwright.

**Use Cases in Career STU:**
- **E2E Testing** - Test complete learner journeys (INTAKE → GOAL_DISCOVERY → PATHWAY → LEARNING)
- **UI Regression Testing** - Ensure UI changes don't break existing functionality
- **Performance Testing** - Monitor page load times and interaction responsiveness
- **Accessibility Testing** - Verify WCAG compliance and screen reader compatibility

**How to Use:**
```bash
# Trigger the skill:
/webapp-testing

# Example prompts:
"Test the learner registration and RIASEC assessment flow"
"Create E2E tests for pathway creation and skill tracking"
"Test the Streamlit UI navigation and state management"
```

**Capabilities:**
- Automated browser testing with Playwright
- Screenshot capture for debugging
- Network request monitoring
- Console log analysis
- Multi-browser testing

---

### 4. Canvas Design (`canvas-design`)

**Purpose:** Generate visual artifacts like posters, infographics, and stylized documents for course content.

**Use Cases in Career STU:**
- **Course Material Design** - Visually engaging posters and infographics for learning content
- **RIASEC Type Cards** - Beautiful visual representations of the 6 RIASEC types
- **Career Pathway Visualizations** - Infographic-style pathway maps
- **Achievement Certificates** - Completion certificates for milestones
- **Marketing Materials** - Posters promoting Career STU features

**How to Use:**
```bash
# Trigger the skill:
/canvas-design

# Example prompts:
"Create an infographic explaining the RIASEC framework"
"Design a completion certificate for finishing a learning pathway"
"Generate a poster visualizing career progression in data science"
```

**Outputs:**
- PDF and PNG documents
- High-quality visual design
- Professional typography and layouts
- Print and web-ready formats

---

## 🎓 Integration with Career STU Modes

### INTAKE Mode
- **frontend-design**: Beautiful onboarding UI
- **canvas-design**: Welcome materials and guides

### GOAL_DISCOVERY Mode
- **frontend-design**: Interactive RIASEC assessment interface
- **web-artifacts-builder**: Job market exploration widgets
- **canvas-design**: RIASEC type visualization cards

### PATHWAY Mode
- **frontend-design**: Course creation and pathway builder UI
- **web-artifacts-builder**: Interactive skill gap visualizations
- **canvas-design**: Pathway infographics and roadmaps

### LEARNING Mode
- **frontend-design**: Engaging learning dashboard
- **web-artifacts-builder**: Interactive exercises and simulations
- **canvas-design**: Visual learning materials and certificates
- **webapp-testing**: E2E testing of learning experience

---

## 🚀 Getting Started with Skills

### 1. Using Skills in Claude Code

Skills are automatically available in Claude Code. Simply invoke them:

```bash
/frontend-design     # Create UI components
/web-artifacts-builder  # Build interactive artifacts
/webapp-testing      # Run automated tests
/canvas-design       # Generate visual materials
```

### 2. Example Workflows

#### Workflow 1: Create Learning Module
```
1. /canvas-design - Create infographic explaining the concept
2. /web-artifacts-builder - Build interactive practice widget
3. /frontend-design - Design the module UI wrapper
4. /webapp-testing - Test the complete module flow
```

#### Workflow 2: Build RIASEC Assessment
```
1. /frontend-design - Create beautiful assessment interface
2. /web-artifacts-builder - Add interactive result visualization
3. /canvas-design - Generate RIASEC type cards
4. /webapp-testing - Test assessment flow and scoring
```

#### Workflow 3: Pathway Creation Interface
```
1. /frontend-design - Design pathway builder UI
2. /web-artifacts-builder - Add drag-and-drop skill ordering
3. /canvas-design - Create pathway overview poster
4. /webapp-testing - Test pathway CRUD operations
```

---

## 📊 Skill Dependencies

Each skill may require specific tools or libraries:

### Frontend Design
- React, TypeScript
- Tailwind CSS
- Modern browser

### Web Artifacts Builder
- React, TypeScript
- shadcn/ui components
- Tailwind CSS

### Webapp Testing
- Playwright
- Node.js
- Chrome/Firefox/Safari

### Canvas Design
- Modern browser for HTML/SVG rendering
- PDF generation capabilities

---

## 🔧 Development Tips

### Best Practices

1. **Use Frontend Design for UI shells** - Create the overall interface structure
2. **Use Web Artifacts Builder for interactivity** - Add complex interactive components
3. **Use Canvas Design for static visuals** - Generate beautiful graphics and documents
4. **Use Webapp Testing throughout** - Ensure quality with continuous testing

### When to Use Which Skill

| Need | Use This Skill |
|------|----------------|
| React component or page | `frontend-design` |
| Interactive widget/simulation | `web-artifacts-builder` |
| Automated test | `webapp-testing` |
| Poster/certificate/infographic | `canvas-design` |

---

## 📝 Contributing

When contributing to Career STU, leverage these skills:

- **Feature Development**: Start with `frontend-design` for UI mockups
- **Interactive Features**: Use `web-artifacts-builder` for complex widgets
- **Testing**: Always add tests with `webapp-testing`
- **Documentation**: Create visual guides with `canvas-design`

---

## 🔗 Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Career STU Documentation](../../../CLAUDE.md)
- [Playwright Documentation](https://playwright.dev)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)

---

## 📞 Support

For questions about these skills:
- Check the individual skill's README in its directory
- Open an issue on the Career STU repository
- Refer to Anthropic's skills documentation

---

**Note:** These skills are sourced from [Anthropic's Skills Repository](https://github.com/anthropics/skills) and integrated into Career STU to enhance the learning experience.
