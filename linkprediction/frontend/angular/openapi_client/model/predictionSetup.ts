/**
 * SNA Link Prediction
 * Social-Network-Analysis Link Prediction Tool.
 *
 * The version of the OpenAPI document: 1.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */
import { Predictor } from './predictor';
import { EvaluationSetup } from './evaluationSetup';


export interface PredictionSetup { 
    selected_predictors: Array<Predictor>;
    evaluation_setup: EvaluationSetup;
}
