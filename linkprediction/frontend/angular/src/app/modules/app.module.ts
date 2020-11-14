import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { CoreModule } from '../core/core.module';
import { LinkPredictionModule } from './link-prediction/link-prediction.module';
import { GraphVisualizationModule } from './graph-visualization/graph-visualization.module';
import { EvaluationModule } from './evaluation/evaluation.module';
import { AppComponent } from './app.component';
import { ApiModule, BASE_PATH } from 'openapi_client';
import { environment } from 'src/environments/environment';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ProjectDetailComponent } from './dashboard/project-detail/project-detail.component';
import { ProjectTileComponent } from './dashboard/project-tile/project-tile.component';
import { ProjectAddComponent } from './dashboard/project-add/project-add.component';
import { FormsModule } from '@angular/forms';
import { SharedModule } from '../shared/shared.module';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    ProjectDetailComponent,
    ProjectTileComponent,
    ProjectAddComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    AppRoutingModule,
    ApiModule,
    CoreModule,
    LinkPredictionModule,
    GraphVisualizationModule,
    EvaluationModule,
    SharedModule
  ],
  providers: [{ provide: BASE_PATH, useValue: environment.API_BASE_PATH }],
  bootstrap: [AppComponent]
})
export class AppModule { }
