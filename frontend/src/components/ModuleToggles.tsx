import React from 'react';

interface Module {
  id: string;
  name: string;
  description: string;
  icon: string;
}

const MODULES: Module[] = [
  {
    id: 'ambiguity',
    name: 'Ambiguity Analysis',
    description: 'Detect vague terms, weak modals, and calculate Requirement Quality Index (RQI).',
    icon: '🔍',
  },
  {
    id: 'classification',
    name: 'FR/NFR Classification',
    description: 'Classify requirements into Functional and Non-Functional categories.',
    icon: '🏷️',
  },
  {
    id: 'uml',
    name: 'UML Extraction',
    description: 'Automatically generate Use Case diagrams from requirement text.',
    icon: '📊',
  },
];

interface ModuleTogglesProps {
  selectedModules: string[];
  onChange: (modules: string[]) => void;
}

const ModuleToggles: React.FC<ModuleTogglesProps> = ({ selectedModules, onChange }) => {
  const toggleModule = (id: string) => {
    if (selectedModules.includes(id)) {
      onChange(selectedModules.filter((m) => m !== id));
    } else {
      onChange([...selectedModules, id]);
    }
  };

  return (
    <div className="toggle-group">
      {MODULES.map((module) => (
        <div
          key={module.id}
          className={`toggle-card ${selectedModules.includes(module.id) ? 'active' : ''}`}
          onClick={() => toggleModule(module.id)}
        >
          <span style={{ fontSize: '1.5rem' }}>{module.icon}</span>
          <div className="toggle-info">
            <h4>{module.name}</h4>
            <p>{module.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ModuleToggles;
