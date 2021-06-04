This is a docker container to generate a GraphViz directional graph of Yoga Asanas that work well together. This is determined from the yoga_asanas.yaml file.

You can build the docker container locally by doing:

```shell
$ make build
```


From there, you can run:

```shell
$ docker run -v /tmp:/data -e EXPERIENCE_LEVELS="Beginner" -e INTENSITY_LEVELS="Low" -e STRENGTH_AREAS="Back,Abdomen" -e MOBILITY_AREAS="Back,Abdomen" --rm yoga_asana_graph:1.0.0
$ ls -l /tmp/yoga_graph.*
  36K -rw-r--r--. 1 nobody nobody  35K Jun  4 13:11 /tmp/yoga_graph.dot
1000K -rw-r--r--. 1 nobody nobody 999K Jun  4 13:11 /tmp/yoga_graph.png
```

From here, open the PNG file in your favorite image viewer.

Have fun.

---
Graphviz: https://graphviz.org/