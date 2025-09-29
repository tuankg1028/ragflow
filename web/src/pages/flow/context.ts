import { LuminationNodeType } from '@/interfaces/database/flow';
import { createContext } from 'react';

export const FlowFormContext = createContext<LuminationNodeType | undefined>(
  undefined,
);
