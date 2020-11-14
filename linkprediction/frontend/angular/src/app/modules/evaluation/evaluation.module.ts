import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EvaluationComponent } from './evaluation.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SharedModule } from 'src/app/shared/shared.module';
import { NgMultiSelectDropDownModule } from 'ng-multiselect-dropdown';
import { RocChartComponent } from './roc-chart/roc-chart.component';



@NgModule({
  declarations: [EvaluationComponent, RocChartComponent],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    SharedModule,
    NgMultiSelectDropDownModule.forRoot(),
  ],
  exports: [EvaluationComponent]
})
export class EvaluationModule { }
