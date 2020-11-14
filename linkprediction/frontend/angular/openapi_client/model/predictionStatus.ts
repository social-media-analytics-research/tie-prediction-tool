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


export interface PredictionStatus { 
    id: string;
    timestamp: Date;
    current_step: number;
    max_steps: number;
    current_step_name: string;
    state: PredictionStatus.StateEnum;
}
export namespace PredictionStatus {
    export type StateEnum = 'Waiting' | 'Processing' | 'Finished' | 'Failed';
    export const StateEnum = {
        Waiting: 'Waiting' as StateEnum,
        Processing: 'Processing' as StateEnum,
        Finished: 'Finished' as StateEnum,
        Failed: 'Failed' as StateEnum
    };
}

