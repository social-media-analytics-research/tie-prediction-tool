import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GraphVisualizationComponent } from './graph-visualization.component';
import { FormsModule } from '@angular/forms';
import { SharedModule } from 'src/app/shared/shared.module';



@NgModule({
  declarations: [GraphVisualizationComponent],
  imports: [
    CommonModule,
    FormsModule,
    SharedModule
  ],
  exports: [GraphVisualizationComponent]
})
export class GraphVisualizationModule { }
