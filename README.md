# haseiq_connect

This Python package allows to read data from a Hase© wood stove.

## IQ version

It looks there's two different versions of IQ systems

- The old one is working with the `Flamemonitor` app

- he new one is working with the `Hase IQ` app

*This lib only works with the old version.*

## Usage

```python
import haseiq_connect

client = haseiq_connect.Client("192.168.1.165")
print(client.get_temperature()) # Get the current temperture inside the wood stove
print(client.get_phase()) # Get the wood stove's current phase (see README phases definitions)
print(client.get_performance()) # Get the current fire performance
print(client.get_minimal_temp_percent()) # Get the temperature percentage of the minimal target temperature
```

## Stove phase

The stove has 5 different phases

- *0*: No fire inside the stove

- *1*: Fire started inside the stove and temperature increasing to reach minimal efficiency level

- *2*: Fire started inside the stove and minimal efficiency temperature reached

- *3*: Fire started inside the stove and need wood

- *4*: The fire is dying out
