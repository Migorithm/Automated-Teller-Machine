# Requirement

At least the following flow should be implemented:<br>

Insert Card => PIN number => Select Account => See Balance/Deposit/Withdraw<br>

For simplification, there are only 1 dollar bills in this world, no cents.<br>

Thus account balance can be represented in integer.<br>

Your code doesn't need to integrate with a real bank system, <br>

but keep in mind that we may want to integrate it with a real bank system in the future. <br>

It doesn't have to integrate with a real cash bin in the ATM, <br>

but keep in mind that we'd want to integrate with that in the future. <br>

And even if we integrate it with them, we'd like to test our code. <br>

Implementing bank integration and ATM hardware like cash bin and card reader is not a scope of this task, <br>

but testing the controller part (not including bank system, cash bin etc) is within the scope.<br>



A bank API wouldn't give the ATM the PIN number, <br>

but it can tell you if the PIN number is correct or not.<br>

Based on your work, another engineer should be able to implement the user interface. <br>

You don't need to implement any REST API, RPC, network communication etc, <br>

but just functions/classes/methods, etc.<br>


You can simplify some complex real world problems if you think it's not worth illustrating in the project.<br>



## Set up
```sh
pip install poetry
poetry install
```

## Test
```sh
pytest
```

## Design concern
As the given assignment pertains to monetery transactions,<br><br>
I thought it's highly likely that there must be a demand for event-sourcing in the future.<br><br>
Therefore, model design adopted was the *event-sourced model*, so it's versioned, domain event-triggering.<br><br>
On top of that, outbox pattern was briefly introduced for the system to be able to reliably<br><br>
notify other services of what happend.<br><br>
The operational processing in service_layer was put in one transaction with due regard to ACID.<br><br>











