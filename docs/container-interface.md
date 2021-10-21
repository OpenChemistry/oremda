Operator Container Interface
----------------------------

In order for a container to be used with OREMDA is must contain the right metadata
to describing the operations it provides and the expected inputs and output. OREMDA
uses labels attached to the container to convey this information.

The format of the support is labels is as follows:

- `oremda.name` - The name of the operator.
- `oremda.description` - A human readable description of the operator. Used within the
UI to describe the operator.
- `oremda.ports.input.<port_name>` - The data type for input port name `<port_name>`.
- `oremda.ports.output.<port_name>` - The data type for output port name `<port_name>`.
- `oremda.metadata.<key>` - This can be used to attach any custom metadata to the operator.

Here is an example adding labels in a Dockerfile:

```
LABEL oremda.name="gaussian_blur" \
      oremda.description="Apply a Gaussian filter" \
      oremda.ports.input.image.type="data" \
      oremda.ports.output.image.type="data"

```