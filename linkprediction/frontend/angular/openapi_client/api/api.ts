export * from './networks.service';
import { NetworksService } from './networks.service';
export * from './prediction.service';
import { PredictionService } from './prediction.service';
export * from './projects.service';
import { ProjectsService } from './projects.service';
export const APIS = [NetworksService, PredictionService, ProjectsService];
