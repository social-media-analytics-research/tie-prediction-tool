import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoadingSpinnerComponent } from './loading-spinner/loading-spinner.component';
import { PredictionSpinnerComponent } from './prediction-spinner/prediction-spinner.component';



@NgModule({
  declarations: [LoadingSpinnerComponent, PredictionSpinnerComponent],
  imports: [
    CommonModule
  ],
  exports: [LoadingSpinnerComponent, PredictionSpinnerComponent]
})
export class SharedModule { }
