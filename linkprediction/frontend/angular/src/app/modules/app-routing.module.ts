import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { LinkPredictionComponent } from './link-prediction/link-prediction.component';
import { GraphVisualizationComponent } from './graph-visualization/graph-visualization.component';
import { EvaluationComponent } from './evaluation/evaluation.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProjectAddComponent } from './dashboard/project-add/project-add.component';
import { ProjectDetailComponent } from './dashboard/project-detail/project-detail.component';
import { PredictorCreatorComponent } from './link-prediction/predictor-creator/predictor-creator.component';
import { ClassifierDetailsComponent } from './link-prediction/classifier-details/classifier-details.component';
import { ClassifierHyperparametersComponent } from './link-prediction/classifier-hyperparameters/classifier-hyperparameters.component';
import { AttributeWeightingsComponent } from './link-prediction/attribute-weightings/attribute-weightings.component';

const routes: Routes = [
  {path: 'dashboard', component: DashboardComponent},
  {path: 'project', component: ProjectAddComponent},
  {path: 'project/:project_id', component: ProjectDetailComponent},
  {path: 'project/:project_id/prediction', component: LinkPredictionComponent},
  {path: 'project/:project_id/prediction/predictor/add', component: PredictorCreatorComponent},
  {path: 'project/:project_id/prediction/classifier/detail', component: ClassifierDetailsComponent},
  {path: 'project/:project_id/prediction/classifier/hyperparameters', component: ClassifierHyperparametersComponent},
  {path: 'project/:project_id/prediction/attribute_weightings', component: AttributeWeightingsComponent},
  {path: 'visualization', component: GraphVisualizationComponent},
  {path: 'evaluation', component: EvaluationComponent},
  {path: '', redirectTo: '/dashboard', pathMatch: 'full'},
  {path: '**', redirectTo: '/dashboard', pathMatch: 'full'}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
