# Greenchoice Variable Tariffs Sensor for Home Assistant

Retrieve Variable Tariffs from the Greenchoice API based on your electrical and/or natural gas connection.

### Installation

Copy the `custom_components/greenchoice_variable_tariffs/` folder to `<config_dir>/custom_components/greenchoice_variable_tariffs/`.

Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: greenchoice_variable_tariffs
    postal_code: 9999ZZ
    use_electricity: true
    use_low_tariff: true
    use_gas: true
```

### Configuration

The `greenchoice_variable_tariffs` sensor platform accepts the following configuration fields:
| Key             	| Type    	| Values        	| Required              	| Explanation                                                                                                                                                                       	            |
|-----------------	|---------	|---------------	|-----------------------	|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	            |
| postal_code     	| String  	| 9999ZZ        	| Yes                   	| A Dutch postal code in the format of four digits and two letters with no space(s)                                                                                                 	            |
| use_electricity 	| Boolean 	| true or false 	| No, defaults to true  	| Indicates that you consume Greenchoices electricity. <br><br> Set this to true when you use either a single or double electricity meter.                                                          |
| use_low_tariff  	| Boolean 	| true or false 	| No, defaults to true  	| Indicates that your electricity meter uses a low tariff. <br><br> Set this to true when you use a double electricity meter. <br><br> Set this to false when you use a single electricity meter. 	|
| use_gas         	| Boolean 	| true or false 	| No, defaults to false 	| Indicates that you consume Greenchoices natural gas.                                                                                                                              	            |