import cv2
from detector import Detector

detector = Detector("model.pt")

# Process results list
for result in detector("data"):
    boxes = result.boxes  # Boxes object for bbox outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Class probabilities for classification outputs

    print(f"========== {len(result.boxes)} détection(s) sur {result.path} ==========")
    if len(result.boxes) == 0:
        print(">>> No litter found <<<")
    else:
        for box in boxes:
            print("Probability :", box.conf[0])
        cv2.imwrite("result.png", result.plot())

    print("\n")