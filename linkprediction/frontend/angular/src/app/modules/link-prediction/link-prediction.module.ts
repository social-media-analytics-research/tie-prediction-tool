import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';

import {LinkPredictionComponent} from './link-prediction.component';
import {PredictorParametersComponent} from './predictor-parameters/predictor-parameters.component';
import {PredictorDynamicFormComponent} from './predictor-dynamic-form/predictor-dynamic-form.component';
import {PredictorCreatorComponent} from './predictor-creator/predictor-creator.component';
import {SharedModule} from 'src/app/shared/shared.module';
import {ClassifierDetailsComponent} from './classifier-details/classifier-details.component';
import {ClassifierHyperparametersComponent} from './classifier-hyperparameters/classifier-hyperparameters.component';
import {AttributeWeightingsComponent} from './attribute-weightings/attribute-weightings.component';
import {NgxBootstrapSliderModule} from 'ngx-bootstrap-slider';


@NgModule({
  declarations: [
    LinkPredictionComponent,
    PredictorParametersComponent,
    PredictorDynamicFormComponent,
    PredictorCreatorComponent,
    ClassifierDetailsComponent,
    ClassifierHyperparametersComponent,
    AttributeWeightingsComponent],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    SharedModule,
    NgxBootstrapSliderModule
  ],
  exports: [LinkPredictionComponent]
})
export class LinkPredictionModule {
}
